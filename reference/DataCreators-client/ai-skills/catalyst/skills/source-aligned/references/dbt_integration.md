# Integration dbt Model Generation Prompt

Generate an integration dbt model with column transformations and checksum calculation.

## Input

Read from source.yml:
- `columns`: All column mappings with source_name, target_name, data types
- `sources`: Source table name (for ref to staging model)
- `target_table`: Target table name
- `target_schema`: Target schema

## Output Structure

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        materialized = 'view',
    )
}}

WITH cte AS (
    SELECT
        {column_selections_with_casts_and_aliases}
    FROM {{ ref("stage_{source_table}") }}
)
SELECT
    cte.*,
    sha1(concat_ws('|', 
        {coalesce_cast_for_each_column}
    )) as dl_checksum_value
FROM cte
```

## Column Selection Rules

For each column in source.yml:

1. **If source_name != target_name**: Alias it
   ```sql
   SourceColumn as target_column,
   ```

2. **If source_data_type != target_data_type**: Cast it
   ```sql
   cast(source_column as {target_data_type}) as target_column,
   ```

3. **If source has special characters or spaces**: Quote it
   ```sql
   "Org Short Name" as org_short_name,
   ```

4. **If column starts with hyphen**: Remove it
   ```sql
   -column_name → column_name
   ```

## Checksum Calculation

Generate `dl_checksum_value` using SHA1 of all columns:

```sql
sha1(concat_ws('|', 
    coalesce(cast(column1 as string), ''),
    coalesce(cast(column2 as string), ''),
    ... for all columns ...
)) as dl_checksum_value
```

## Example Output

```sql
{{
    config(
        schema = "cspn_work2_"|string + target.name,
        materialized = 'view',
    )
}}

WITH cte AS (
    SELECT
        OfficershipID as officershipid,
        Initials as initials,
        AssociateNumber as associatenumber,
        Status as status,
        FirstName as firstname,
        LastName as lastname,
        "Org Short Name" as org_short_name,
        "Position Title" as position_title,
        EntityTypeCode as entitytypecode,
        Entity as entity,
        "Group" as group,
        Title as title,
        cast(StartDate as string) as startdate,
        cast(EndDate as string) as enddate,
        Abbreviation as abbreviation
    FROM {{ ref("stage_officerships") }}
)
SELECT
    cte.*,
    sha1(concat_ws('|', 
        coalesce(cast(cte.officershipid as string), ''),
        coalesce(cast(cte.initials as string), ''),
        coalesce(cast(cte.associatenumber as string), ''),
        coalesce(cast(cte.status as string), ''),
        coalesce(cast(cte.firstname as string), ''),
        coalesce(cast(cte.lastname as string), ''),
        coalesce(cast(cte.org_short_name as string), ''),
        coalesce(cast(cte.position_title as string), ''),
        coalesce(cast(cte.entitytypecode as string), ''),
        coalesce(cast(cte.entity as string), ''),
        coalesce(cast(cte.group as string), ''),
        coalesce(cast(cte.title as string), ''),
        coalesce(cast(cte.startdate as string), ''),
        coalesce(cast(cte.enddate as string), ''),
        coalesce(cast(cte.abbreviation as string), '')
    )) as dl_checksum_value
FROM cte
```

## File Naming

Save as: `models/integration/int_{target_table}.sql`

Example: `models/integration/int_officerships_v4.sql`

## Validation

- All columns from source.yml are included
- Proper casting applied where types differ
- All columns included in checksum calculation
- References staging model correctly
