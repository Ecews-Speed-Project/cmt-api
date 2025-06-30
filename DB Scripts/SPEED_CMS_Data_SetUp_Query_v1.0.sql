-- create cmt and insert data from the state linelist
CREATE TABLE cms.cmt (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL,
    state NVARCHAR(100) NOT NULL,
    facility_name NVARCHAR(200) NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE()
);

INSERT INTO cms.cmt(name, state, facility_name)
select distinct CaseManagementTeamNameIdentifier, 
	State,
	FacilityName
	from cms.case_manager_list cml2;


-- create case mangers table
CREATE TABLE cms.case_managers (
    id NVARCHAR(100) PRIMARY KEY,
    fullname NVARCHAR(100) NOT NULL,
    role NVARCHAR(100) NOT NULL,
    cmt NVARCHAR(100) NOT NULL,
    state INT NOT NULL,
    facilities NVARCHAR(100) NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE()
);


INSERT INTO [cms].[case_managers]
           ([id]
           ,[fullname]
           ,[role]
           ,[cmt]
           ,[state]
           ,[facilities])
SELECT 
    cm.CasemanagementID,
    cm.NameofCaseManager,

    -- Distinct role IDs concatenated
    (
        SELECT STRING_AGG(CAST(r.id AS NVARCHAR(MAX)), ',')
        FROM (
            SELECT DISTINCT r.id
            FROM [Speed].[cms].[case_manager_list] cml
            INNER JOIN [cms].[cm_roles] r ON cml.roles = r.role
            WHERE cml.CasemanagementID = cm.CasemanagementID
        ) AS r
    ) AS role,

    -- Distinct CMT names concatenated
    (
       
            SELECT DISTINCT c.name
            FROM [Speed].[cms].[case_manager_list] cml
            INNER JOIN [cms].[cmt] c ON cml.CasemanagementTeamNameIdentifier = c.name
            WHERE cml.CasemanagementID = cm.CasemanagementID
        
    ) AS cmt,

    (
		SELECT DISTINCT s.StateId FROM [SPEED].[cms].case_manager_list AS cml
		INNER JOIN [SPEED].[dbo].[State] s ON cml.State = s.StateName
		WHERE cml.CasemanagementID = cm.CasemanagementID
	) as state,

    -- Distinct facility IDs concatenated
    (
        SELECT STRING_AGG(CAST(fac_sub.facilityId AS NVARCHAR(MAX)), ',')
        FROM (
            SELECT DISTINCT f.facilityId
            FROM [Speed].[cms].[case_manager_list] cml
            INNER JOIN [dbo].[facilities] f ON cml.DatimCode = f.DatimCode
            WHERE cml.CasemanagementID = cm.CasemanagementID
        ) AS fac_sub
    ) AS facility_name

FROM (
    SELECT DISTINCT CasemanagementID, NameofCaseManager, State
    FROM [Speed].[cms].[case_manager_list]
) AS cm
ORDER BY cm.CasemanagementID;


-- create roles table and populate it with roles from the list from the states
CREATE TABLE cms.cm_roles (
    id INT IDENTITY(1,1) PRIMARY KEY,
    role NVARCHAR(100) NOT NULL,
    created_at DATETIME2 DEFAULT GETUTCDATE()
);

INSERT INTO cms.cm_roles(role)
SELECT DISTINCT roles from cms.case_manager_list;