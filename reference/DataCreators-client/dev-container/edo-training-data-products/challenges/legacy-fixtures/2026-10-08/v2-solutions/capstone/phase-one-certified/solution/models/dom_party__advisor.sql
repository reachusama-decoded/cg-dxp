select * from {{ ref('advisors') }} where advisor_id>0
