config_pnl = (
    [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 33,
     34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 46, 47, 48, 151],
    ['Index', 'Anaplant_Index', 'PBI_Index', 'K_Nature', 'Actual_LY_01', 'Actual_LY_02', 'Actual_LY_03',
     'Actual_LY_04', 'Actual_LY_05', 'Actual_LY_06', 'Actual_LY_07', 'Actual_LY_08', 'Actual_LY_09',
     'Actual_LY_10', 'Actual_LY_11', 'Actual_LY_12', 'Budget_CY_01', 'Budget_CY_02', 'Budget_CY_03',
     'Budget_CY_04', 'Budget_CY_05', 'Budget_CY_06', 'Budget_CY_07', 'Budget_CY_08', 'Budget_CY_09',
     'Budget_CY_10', 'Budget_CY_11', 'Budget_CY_12', 'Actual_CY_01', 'Actual_CY_02', 'Actual_CY_03',
     'Actual_CY_04', 'Actual_CY_05', 'Actual_CY_06', 'Actual_CY_07', 'Actual_CY_08', 'Actual_CY_09',
     'Actual_CY_10', 'Actual_CY_11', 'Actual_CY_12', 'Actual_NY_01', 'Actual_NY_02', 'Actual_NY_03', 'CostCenter_Code'],
    8,
    "R_PL_FI")
config_ic = (
    [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 22, 23, 24, 25, 26,
        27, 28, 29, 30, 31, 32, 33, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 49, 50, 51],
    ['INDEX', 'ANAPLAN_INDEX', 'PBI_INDEX', 'BU', 'COSTCENTER', 'ACCOUNT', 'IC_PARTNER',
     'Actual_LY_01', 'Actual_LY_02', 'Actual_LY_03', 'Actual_LY_04', 'Actual_LY_05', 'Actual_LY_06',
     'Actual_LY_07', 'Actual_LY_08', 'Actual_LY_09', 'Actual_LY_10', 'Actual_LY_11', 'Actual_LY_12',
     'Budget_CY_01', 'Budget_CY_02', 'Budget_CY_03', 'Budget_CY_04', 'Budget_CY_05', 'Budget_CY_06',
     'Budget_CY_07', 'Budget_CY_08', 'Budget_CY_09', 'Budget_CY_10', 'Budget_CY_11', 'Budget_CY_12',
     'Actual_CY_01', 'Actual_CY_02', 'Actual_CY_03', 'Actual_CY_04', 'Actual_CY_05', 'Actual_CY_06',
     'Actual_CY_07', 'Actual_CY_08', 'Actual_CY_09', 'Actual_CY_10', 'Actual_CY_11', 'Actual_CY_12',
     'Actual_NY_01', 'Actual_NY_02', 'Actual_NY_03'],
    9,
    "R_IC")
config_kpi_pyramid = (
    'B:Z',
    ["BU", "VERSION", "PERIOD", "COST_CENTER", "PEOPLE_TYPE", "LEVEL_SENIORITY",
     "ENDOFMONTH_FTE", "BILLABLE_DAYS", "INTERNAL_PROJECTS", "PRE_SALES_DAYS", "TRAINING_DAYS", "INACTIVITY_DAY",
        "HOLIDAYS", "SICK_DAYS", "TOTAL_DAYS", "OCCUPANCY_RATE", "SRVC_SALES_BEF_BONIMALI", "DAILY_RATE",
        "ANNUAL_DIRECT_COSTS", "ANNUAL_PRODUCTION_DAYS", "DAILY_COST", "DAILY_MARGIN", "IN", "OUT", "TRANSFER_PROMO"],
    15,
    "R_KPI_PYRAMID")
config_license_maint = (
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,
        14, 15, 16, 17, 18, 19, 20, 21, 41],
    ["BU", "VERSION", "PERIOD", "SOFTWARE_PARTNERS",
     "REV_LIC_PERPETUAL", "REV_LIC_NEW_SUBSCRIPTION", "REV_LIC_IC_SALES", "REV_MAINT_1STYEAR",
     "REV_MAINT_IC_SALES", "REV_LIC_RENEWED_SUBSCRIPTION", "REV_MAINT_RENEWAL", "REV_LIC_REFERRALS", "TOTAL_REVENUE",
     "CP_LICPUR_PERPETUAL", "CP_LICPUR_NEW_SUBSCRIPTION", "CP_LIC_IC_PUR", "CP_MAINTPUR_1STYEAR",
     "CP_MAINT_IC_SUBCONTRACT", "CP_LICPUR_RENEWED_SUBSCRIPTION", "CP_MAINT_RENEWAL", "TOTAL_COST",
     "CHURN_RATE"],
    12,
    "R_LIC_MAINT")
config_client = (
    'B:O',
    ['BU', 'SCENARIO', 'PERIOD', 'CLIENT_NAME', 'BU_CLIENT', 'BU_PERIOD', 'TOTAL_SIGNING',
        'ACTUAL', 'BACKLOG', 'W_PIPELINE', 'BLUE_SKY', 'TOTAL', 'MARGIN', 'MARGIN_PERC'],
    14,
    "R_CLI")
config_revenue_dist = (
    'B:N',
    ['BU', 'SCENARIO', 'PERIOD', 'REVENUE_TYPE', 'REVENUE_SUB_TYPE', 'TOTAL_SIGNING', 'ACTUAL', 'BACKLOG', 'W_PIPELINE',
     'BACKLOG_N', 'W_PIPELINE_N', 'BACKLOG_N1', 'W_PIPELINE_N1'],
    14,
    "R_REVDIS")
config_backlog = (
    [0, 1, 2, 3, 4, 5, 6, 7],
    ['INDEX', 'BU', 'SCENARIO', 'PERIOD', 'NATURE_GROUP',
     'NATURE_SUB_GROUP', 'BACKLOG', 'WEIGHTED_PIPELINE'],
    13,
    "R_BACKLOG")
config_project_pro = (
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ['PROJECT_NAME', 'CLIENT', 'BU', 'CURRENCY', 'PROJECT_STATUS', 'COL_G',
     'PERIOD', 'PROJECT_REVENUE', 'PROJECT_BONIMALI', 'PROJECT_COST'],
    14,
    "R_PROJECT_PRO")
config_project_pl = (
    [1, 2, 3, 4, 5, 6, 7, 8, 9],
    ['PROJECT_NAME', 'CLIENT', 'BU', 'CURRENCY', 'COL_F',
     'SCENARIO', 'PERIOD', 'PROJECT_REVENUE', 'PROJECT_COST'],
    14,
    "R_PROJECT_PL")
config_project_cc = (
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    ['PROJECT_NAME', 'CLIENT', 'BU', 'CURRENCY', 'COL_F', 'COL_G',
     'PERIOD', 'INVOICES_PAID', 'INVOICES_DUE', 'INVOICES_OVERDUE'],
    14,
    "R_PROJECT_CC")

# Budget config file
config_budget_pl = (
    [0, 1, 2, 4, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 151],
    ['INDEX', 'ANAPLANT_INDEX', 'PBI_INDEX', 'K_NATURE', 'BUDGET_CY_01', 'BUDGET_CY_02', 'BUDGET_CY_03', 'BUDGET_CY_04', 'BUDGET_CY_05',
     'BUDGET_CY_06', 'BUDGET_CY_07', 'BUDGET_CY_08', 'BUDGET_CY_09', 'BUDGET_CY_10', 'BUDGET_CY_11', 'BUDGET_CY_12', 'COSTCENTER_CODE'],
    8,
    "R_BUD_PL")
config_budget_kpi_pyramid = (
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14,
        15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
    ['BU', 'SCENARIO', 'PERIOD', 'COST_CENTER', 'PEOPLE_TYPE', 'LEVEL_SENIORITY',
     'ENDOFMONTH_FTE', 'BILLABLE_DAYS', 'INTERNAL_PROJECT', 'PRE_SALES_DAYS', 'TRAINING_DAYS', 'INACTIVITY_DAYS', 'HOLIDAYS',
     'SICK_DAYS', 'TOTAL_DAYS', 'OCCUPANCY_RATE', 'SRVC_SALES_BEF_BONIMALI',  'DAILY_RATE', 'ANNUAL_DIRECT_COSTS', 'ANNUAL_PRODUCTION_DAYS',
     'DAILY_COST', 'DAILY_MARGIN', 'IN', 'OUT', 'TRANSFER_PROMOTIONS'],
    125,
    "R_BUD_KPI")
config_budget_license_maint = (
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21],
    ['BU', 'VERSION', 'PERIOD', 'SOFTWARE_PARTNERS', 'REV_LIC_PERPETUAL', 'REV_LIC_NEW_SUBSCRIPTION', 'REV_LIC_IC_SALES',
     'REV_MAINT_1STYEAR', 'REV_MAINT_IC_SALES', 'REV_LIC_RENEWED_SUBSCRIPTION', 'REV_MAINT_RENEWAL', 'REV_LIC_REFERRALS', 'TOTAL_REVENUE',
     'CP_LICPUR_PERPETUAL', 'CP_LICPUR_NEW_SUBSCRIPTION', 'CP_LICPUR_IC', 'CP_MAINTPUR_1STYEAR', 'CP_MAINT_IC_SUBCONTRACT',
     'CP_LICPUR_RENEWED_SUBSCRIPTION', 'CP_MAINT_RENEWAL', 'TOTAL_COST'],
    124,
    "R_BUD_LM")
config_budget_client = (
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13],
    ['BU', 'SCENARIO', 'PERIOD', 'CLIENT_NAME', 'PEOPLE_TYPE', 'LEVEL_SENIORITY', 'TOTAL_SIGNING',
     'BACKLOG', 'PIPELINE', 'BLUE_SKY', 'TOTAL', 'MARGIN', 'MARGIN_PERC'],
    44,
    "R_BUD_CLI")
config_budget_revenue_dist = (
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    ['BU', 'SCENARIO', 'PERIOD', 'REVENUE_TYPE', 'REVENUE_SUB_TYPE', 'LEVEL_SENIORITY',
     'TOTAL_SIGNING', 'BACKLOG', 'PIPELINE', 'BLUE_SKY', 'TOTAL'],
    44,
    "R_BUD_REVDIS")
config_budget_signing_pipeline = (
    [1, 2, 3, 4, 5, 6],
    ['BU', 'SCENARIO', 'PERIOD', 'PRODUCTION_PERIOD',
     'BUSINESS_LINE', 'TOTAL_SIGNING'],
    115,
    "R_BUD_SIGPIP")
config_budget_ic = (
    [1, 2, 3, 4, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
    ['BU', 'COST_CENTER', 'ACCOUNT', 'IC_PARTNER', 'BUDGET_CY_01', 'BUDGET_CY_02', 'BUDGET_CY_03', 'BUDGET_CY_04', 'BUDGET_CY_05',
     'BUDGET_CY_06', 'BUDGET_CY_07', 'BUDGET_CY_08', 'BUDGET_CY_09', 'BUDGET_CY_10', 'BUDGET_CY_11', 'BUDGET_CY_12'],
    10,
    "R_BUD_ICDECL")

# FX Rate Exchange
config_fx_rate = (
    [0, 1, 2, 3, 4, 5, 6],
    ["ID", "INPUTCURRENCY", "CURRENCYPAIR", "MONTHYEAR",
     "ACTUAL_LY", "BUDGET_CY", "ACTUAL_CY"],
    2,
    "TEST_R_FX_RATES")

# Ecovadis
config_ecovadis = (
    [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
    ['MEASURE_CODE', 'MEASURE_ID', 'ECOVADIS_PILAR', 'MEASURE', 'SCOPE', 'UNIT_DESC', 'VALUE_PRIOR_YEAR_3', 'VALUE_PRIOR_YEAR_2',
     'VALUE_PRIOR_YEAR_1', 'COMMENT'],
    11,
    "R_ESG")

# Adjustement
config_adjustement = (
    [0, 1, 3, 4, 6, 7, 10, 11, 12],
    ["INDEX", "MBR_MONTH", "BU", "CURRENCY", "SCENARIO",
     "PERIOD", "AMOUNT", "COMMENTS", "TYPE"],
    0,
    "R_PL_FI_FPA"
)
