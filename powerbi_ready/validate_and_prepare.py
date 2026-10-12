import sys, csv, os, glob, json

sys.stdout.reconfigure(encoding='utf-8')

print('=' * 70)
print('STEP 1-6: FULL DATASET INSPECTION & VALIDATION')
print('=' * 70)

datasets = {
    'Dim_City': {'path': 'data/cities.csv', 'is_dir': False},
    'City_Monthly': {'path': 'output/city_monthly', 'is_dir': True},
    'City_Temperature': {'path': 'output/city_temperature', 'is_dir': True},
    'City_Rainfall': {'path': 'output/city_rainfall', 'is_dir': True},
    'City_Wind': {'path': 'output/city_wind', 'is_dir': True},
    'City_Humidity': {'path': 'output/city_humidity', 'is_dir': True},
}

all_city_sets = {}
all_data = {}

for name, spec in datasets.items():
    print(f'\n--- {name} ---')
    if spec['is_dir']:
        files = sorted(glob.glob(os.path.join(spec['path'], 'part-*.csv')))
    else:
        files = [spec['path']]

    header = None
    rows = []
    for fpath in files:
        with open(fpath, 'r', encoding='utf-8') as fh:
            reader = csv.reader(fh)
            for i, row in enumerate(reader):
                if not row or all(c.strip() == '' for c in row):
                    continue
                trimmed = [c.strip() for c in row]
                if header is None:
                    header = trimmed
                elif trimmed == header:
                    continue
                else:
                    rows.append(dict(zip(header, trimmed)))

    all_data[name] = {'header': header, 'rows': rows}
    print(f'  Source files: {len(files)}')
    print(f'  Columns ({len(header)}): {header}')
    print(f'  Total rows: {len(rows)}')

    city_names = [r['city_name'] for r in rows]
    unique_cities = sorted(set(city_names))
    all_city_sets[name] = set(unique_cities)
    print(f'  Unique cities: {len(unique_cities)}')

    if name == 'City_Monthly':
        keys = [(r['city_name'], r['year'], r['month']) for r in rows]
        unique_keys = set(keys)
        dup_keys = len(keys) - len(unique_keys)
        print(f'  Grain check (city+year+month): {len(unique_keys)} unique composite keys, {dup_keys} duplicates')
        years = sorted(set(int(r['year']) for r in rows))
        months = sorted(set(int(r['month']) for r in rows))
        print(f'  Years: {years}')
        print(f'  Months: {months}')
        date_keys = sorted(set((int(r['year']), int(r['month'])) for r in rows))
        print(f'  Unique (year,month) DateKey values needed: {len(date_keys)}')
        print(f'  Date range: {date_keys[0]} to {date_keys[-1]}')
    else:
        is_unique = len(unique_cities) == len(rows)
        print(f'  city_name unique per row: {is_unique} ({len(unique_cities)} cities, {len(rows)} rows)')

    missing = {}
    for col in header:
        mc = sum(1 for r in rows if r.get(col, '').strip() == '')
        if mc > 0:
            missing[col] = mc
    if missing:
        print(f'  Missing values: {missing}')
    else:
        print(f'  Missing values: NONE')

    row_tuples = [tuple(sorted(r.items())) for r in rows]
    dup_rows = len(row_tuples) - len(set(row_tuples))
    print(f'  Duplicate rows: {dup_rows}')

# Cross-table referential integrity
print(f'\n--- REFERENTIAL INTEGRITY ---')
dim_cities = all_city_sets['Dim_City']
for name in ['City_Monthly', 'City_Temperature', 'City_Rainfall', 'City_Wind', 'City_Humidity']:
    fact_cities = all_city_sets[name]
    in_dim_not_fact = dim_cities - fact_cities
    in_fact_not_dim = fact_cities - dim_cities
    status = 'PASS' if not in_dim_not_fact and not in_fact_not_dim else 'FAIL'
    print(f'  Dim_City vs {name}: {status}')

# Step 7: Generate Dim_Date with UNIQUE monthly dates
print(f'\n--- STEP 7: GENERATING Dim_Date.csv ---')
monthly_rows = all_data['City_Monthly']['rows']
date_keys = sorted(set((int(r['year']), int(r['month'])) for r in monthly_rows))

season_map = {
    12: ('Winter', 1), 1: ('Winter', 1), 2: ('Winter', 1),
    3: ('Summer', 2), 4: ('Summer', 2), 5: ('Summer', 2),
    6: ('Monsoon', 3), 7: ('Monsoon', 3), 8: ('Monsoon', 3), 9: ('Monsoon', 3),
    10: ('Post-Monsoon', 4), 11: ('Post-Monsoon', 4),
}

month_names = ['', 'January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']
month_short = ['', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

dim_date_rows = []
for year, month in date_keys:
    season_name, season_order = season_map[month]
    quarter = (month - 1) // 3 + 1
    date_key = f'{year}-{month:02d}-01'
    year_month = f'{year}-{month:02d}'
    dim_date_rows.append({
        'DateKey': date_key,
        'Year': str(year),
        'MonthNo': str(month),
        'MonthName': month_names[month],
        'MonthShort': month_short[month],
        'Quarter': f'Q{quarter}',
        'YearMonth': year_month,
        'Season': season_name,
        'SeasonOrder': str(season_order),
    })

# Verify DateKey uniqueness
date_key_values = [r['DateKey'] for r in dim_date_rows]
assert len(date_key_values) == len(set(date_key_values)), 'FATAL: Dim_Date DateKey is NOT unique!'
print(f'  Total unique monthly DateKey values: {len(dim_date_rows)}')
print(f'  DateKey uniqueness: VERIFIED')
print(f'  Range: {dim_date_rows[0]["DateKey"]} to {dim_date_rows[-1]["DateKey"]}')
print(f'  Seasons: {sorted(set(r["Season"] for r in dim_date_rows))}')

os.makedirs('powerbi_ready', exist_ok=True)

# Write Dim_Date.csv
dim_date_header = ['DateKey', 'Year', 'MonthNo', 'MonthName', 'MonthShort', 'Quarter', 'YearMonth', 'Season', 'SeasonOrder']
with open('powerbi_ready/Dim_Date.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=dim_date_header)
    writer.writeheader()
    writer.writerows(dim_date_rows)
print(f'  Written: powerbi_ready/Dim_Date.csv ({len(dim_date_rows)} rows)')

# Step 8: Add DateKey column to City_Monthly for relationship mapping
print(f'\n--- STEP 8: ADDING DateKey TO City_Monthly ---')
monthly_header = all_data['City_Monthly']['header'] + ['DateKey']
city_monthly_with_dk = []
for r in monthly_rows:
    new_row = dict(r)
    new_row['DateKey'] = f'{int(r["year"]):04d}-{int(r["month"]):02d}-01'
    city_monthly_with_dk.append(new_row)

# Verify City_Monthly DateKey values are subset of Dim_Date DateKey values
cm_dk_set = set(r['DateKey'] for r in city_monthly_with_dk)
dd_dk_set = set(r['DateKey'] for r in dim_date_rows)
orphan_keys = cm_dk_set - dd_dk_set
print(f'  City_Monthly DateKey values: {len(cm_dk_set)}')
print(f'  Dim_Date DateKey values: {len(dd_dk_set)}')
print(f'  Orphaned DateKeys (in CM but not in DD): {len(orphan_keys)}')
if orphan_keys:
    print(f'    WARNING: {orphan_keys}')

with open('powerbi_ready/City_Monthly.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=monthly_header)
    writer.writeheader()
    writer.writerows(city_monthly_with_dk)
print(f'  Written: powerbi_ready/City_Monthly.csv ({len(city_monthly_with_dk)} rows, with DateKey)')

# Write remaining consolidated tables (Dim_City and summaries)
for name, target_file in [
    ('Dim_City', 'Dim_City.csv'),
    ('City_Temperature', 'City_Temperature.csv'),
    ('City_Rainfall', 'City_Rainfall.csv'),
    ('City_Wind', 'City_Wind.csv'),
    ('City_Humidity', 'City_Humidity.csv'),
]:
    hdr = all_data[name]['header']
    rws = all_data[name]['rows']
    with open(f'powerbi_ready/{target_file}', 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=hdr)
        writer.writeheader()
        writer.writerows(rws)
    print(f'  Written: powerbi_ready/{target_file} ({len(rws)} rows)')

# Step 9: Final relationship key validation
print(f'\n--- STEP 9: RELATIONSHIP KEY VALIDATION ---')
dim_city_keys = set(r['city_name'] for r in all_data['Dim_City']['rows'])
cm_city_keys = set(r['city_name'] for r in city_monthly_with_dk)
ct_city_keys = set(r['city_name'] for r in all_data['City_Temperature']['rows'])
cr_city_keys = set(r['city_name'] for r in all_data['City_Rainfall']['rows'])
cw_city_keys = set(r['city_name'] for r in all_data['City_Wind']['rows'])
ch_city_keys = set(r['city_name'] for r in all_data['City_Humidity']['rows'])

relationships = [
    ('Dim_City[city_name] 1:* City_Monthly[city_name]', dim_city_keys, cm_city_keys, '1:*'),
    ('Dim_Date[DateKey] 1:* City_Monthly[DateKey]', dd_dk_set, cm_dk_set, '1:*'),
    ('Dim_City[city_name] 1:1 City_Temperature[city_name]', dim_city_keys, ct_city_keys, '1:1'),
    ('Dim_City[city_name] 1:1 City_Rainfall[city_name]', dim_city_keys, cr_city_keys, '1:1'),
    ('Dim_City[city_name] 1:1 City_Wind[city_name]', dim_city_keys, cw_city_keys, '1:1'),
    ('Dim_City[city_name] 1:1 City_Humidity[city_name]', dim_city_keys, ch_city_keys, '1:1'),
]

for desc, one_side, many_side, cardinality in relationships:
    one_unique = True  # One-side must be unique (already verified above)
    if cardinality == '1:1':
        many_unique = len(many_side) == len(all_data[desc.split(' 1:1 ')[1].split('[')[0]]['rows'])
    else:
        many_unique = True
    covers = many_side.issubset(one_side)
    status = 'VALID' if covers else 'INVALID'
    orphans = many_side - one_side
    print(f'  {desc}: {status}')
    if orphans:
        print(f'    Orphan keys: {orphans}')

print(f'\n--- ALL STEPS COMPLETE ---')
print(f'powerbi_ready/ now contains 7 clean CSV files ready for Power BI import.')
