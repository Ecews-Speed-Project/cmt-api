-- Drop table if it exists (optional - remove if you want to preserve existing data)
IF OBJECT_ID('cms.performance', 'U') IS NOT NULL
    TRUNCATE TABLE cms.performance;

-- Insert data into the performance table
WITH 
-- Tx_Cur: Patients currently on active treatment
Tx_Cur_CTE AS (
    SELECT cm.id as caseManagerId, COUNT(ll.pepId) as Tx_Cur
	FROM (SELECT DISTINCT id FROM cms.case_managers) cm
	LEFT JOIN LineList as ll on ll.caseManagerId = cm.id
	WHERE ll.currentArtStatus = 'Active'
	GROUP BY cm.id
),

-- IIT: Patients lost to follow up
IIT_CTE AS (
    SELECT cm.id as caseManagerId, COUNT(ll.caseManagerId) as IIT
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN LineList as ll on ll.caseManagerId = cm.id
    WHERE ll.currentArtStatus = 'LTFU' OR ll.currentArtStatus = 'Lost to follow up'
    GROUP BY cm.id
),

-- Dead: Patients reported as deceased
Dead_CTE AS (
    SELECT cm.id as caseManagerId, COUNT(ll.caseManagerId) as Dead
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN LineList as ll on ll.caseManagerId = cm.id
    WHERE ll.currentArtStatus = 'Death'
    GROUP BY cm.id
),

-- Discontinued: Patients who discontinued treatment
Discontinued_CTE AS (
    SELECT cm.id as caseManagerId, COUNT(ll.caseManagerId) as Discontinued
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN LineList as ll on ll.caseManagerId = cm.id
    WHERE ll.currentArtStatus Like '%Discontinue%'
    GROUP BY cm.id
),

-- Transferred Out: Patients transferred to other facilities
TransferredOut_CTE AS (
    SELECT cm.id as caseManagerId, COUNT(ll.caseManagerId) as Transferred_Out
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN LineList as ll on ll.caseManagerId = cm.id
    WHERE ll.currentArtStatus = 'Transferred Out'
    GROUP BY cm.id
),

-- Total Appointments: All scheduled appointments
Appointments_CTE AS (
    SELECT cm.id as caseManagerId, COUNT(dpa.caseManagerId) as appointments_schedule
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN DrugPickupAppointment dpa on dpa.caseManagerId = cm.id
    GROUP BY cm.id
),

-- Appointments Kept: Patients who kept their appointments
AppointmentsKept_CTE AS (
    SELECT cm.id AS caseManagerId, COUNT(DISTINCT ll.pepId) AS appointments_completed
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN LineList ll ON ll.caseManagerId = cm.id
    LEFT JOIN DrugPickupAppointment dpa ON dpa.caseManagerId = ll.caseManagerId AND dpa.pepId = ll.pepId
    WHERE ll.currentArtStatus = 'Active'
    AND ll.pharmacyLastPickupDate > dpa.pharmacyLastPickupDate
    GROUP BY cm.id
),

-- VL Eligible: Patients eligible for viral load testing
VLEligible_CTE AS (
    SELECT cm.id as caseManagerId, COUNT(vla.caseManagerId) as viral_load_eligible
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN VLAppointment vla on vla.caseManagerId = cm.id
    GROUP BY cm.id
),

-- VL Samples Collected: Viral load samples collected
VLCollected_CTE AS (
    SELECT cm.id as caseManagerId, COUNT(DISTINCT ll.pepId) as viral_load_samples
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN LineList ll ON ll.caseManagerId = cm.id
    LEFT JOIN VLAppointment vla ON vla.caseManagerId = cm.id AND vla.pepId = ll.pepId
    WHERE ll.currentArtStatus = 'Active'
    AND ll.lastDateOfSampleCollection > vla.lastDateOfSampleCollection
    GROUP BY cm.id
),

-- Quarter End Dates: Used for viral load calculations
QuarterEndDates AS (
    SELECT
        ll.caseManagerId,
        MAX(DATEADD(day, dpa.daysOfARVRefill, dpa.pharmacyLastPickupDate)) AS lastDateOfQuarter
    FROM LineList ll
    JOIN DrugPickupAppointment dpa ON ll.caseManagerId = dpa.caseManagerId AND ll.pepId = dpa.pepId
    WHERE ll.currentArtStatus = 'Active'
    GROUP BY ll.caseManagerId
),

-- Valid Viral Load: Patients with valid viral load results
ValidVL_CTE AS (
    SELECT
        cm.id AS caseManagerId,
        COUNT(ll.pepId) AS viral_load_results
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN LineList ll ON ll.caseManagerId = cm.id
    LEFT JOIN QuarterEndDates qed ON ll.caseManagerId = qed.caseManagerId
    WHERE ll.currentArtStatus = 'Active'
      AND ll.daysOnART >= 180
      AND ll.dateOfCurrentViralLoad IS NOT NULL
      AND qed.lastDateOfQuarter IS NOT NULL
      AND ll.dateOfCurrentViralLoad >= DATEADD(day, -360, qed.lastDateOfQuarter)
      AND ll.currentViralLoad IS NOT NULL
    GROUP BY cm.id
),

-- Suppressed Viral Load: Patients with suppressed viral load
SuppressedVL_CTE AS (
    SELECT
        cm.id AS caseManagerId,
        COUNT(ll.pepId) AS viral_load_suppressed
    FROM (SELECT DISTINCT id FROM cms.case_managers) cm
    LEFT JOIN LineList ll ON ll.caseManagerId = cm.id
    LEFT JOIN QuarterEndDates qed ON ll.caseManagerId = qed.caseManagerId
    WHERE ll.currentArtStatus = 'Active'
      AND ll.daysOnART >= 180
      AND ll.dateOfCurrentViralLoad IS NOT NULL
      AND qed.lastDateOfQuarter IS NOT NULL
      AND ll.dateOfCurrentViralLoad >= DATEADD(day, -360, qed.lastDateOfQuarter)
      AND ll.currentViralLoad IS NOT NULL
      AND ll.currentViralLoad < CAST(1000 AS FLOAT)
    GROUP BY cm.id
)

-- Insert the combined result into the performance table
INSERT INTO cms.performance(
    CaseManagerID,
    Tx_Cur,
    IIT,
    Dead,
    Discontinued,
    Transferred_Out,
    appointments_schedule,
    appointments_completed,
    appointment_compliance,
    viral_load_eligible,
    viral_load_samples,
    sample_collection_rate,
    viral_load_results,
    viral_load_suppressed,
    suppression_rate,
    final_score
)
SELECT 
    DISTINCT cm.id AS CaseManagerID,
    ISNULL(tc.Tx_Cur, 0) AS Tx_Cur,
    ISNULL(iit.IIT, 0) AS IIT,
    ISNULL(d.Dead, 0) AS Dead,
    ISNULL(disc.Discontinued, 0) AS Discontinued,
    ISNULL(tout.Transferred_Out, 0) AS Transferred_Out,
    ISNULL(appt.appointments_schedule, 0) AS appointments_schedule,
    ISNULL(ak.appointments_completed, 0) AS appointments_completed,
    CASE 
        WHEN ISNULL(appt.appointments_schedule, 0) = 0 THEN 0 
        ELSE CAST(ISNULL(ak.appointments_completed, 0) AS FLOAT) / ISNULL(appt.appointments_schedule, 0) * 100 
    END AS appointment_compliance,
    ISNULL(vle.viral_load_eligible, 0) AS viral_load_eligible,
    ISNULL(vlc.viral_load_samples, 0) AS viral_load_samples,
    CASE 
        WHEN ISNULL(vle.viral_load_eligible, 0) = 0 THEN 0 
        ELSE CAST(ISNULL(vlc.viral_load_samples, 0) AS FLOAT) / ISNULL(vle.viral_load_eligible, 0) * 100 
    END AS sample_collection_rate,
    ISNULL(vvl.viral_load_results, 0) AS viral_load_results,
    ISNULL(svl.viral_load_suppressed, 0) AS viral_load_suppressed,
    CASE 
        WHEN ISNULL(vvl.viral_load_results, 0) = 0 THEN 0 
        ELSE CAST(ISNULL(svl.viral_load_suppressed, 0) AS FLOAT) / ISNULL(vvl.viral_load_results, 0) * 100 
    END AS suppression_rate,
    -- Calculate final_score using the actual expressions instead of column aliases
    (
        (CASE 
            WHEN ISNULL(appt.appointments_schedule, 0) = 0 THEN 0 
            ELSE CAST(ISNULL(ak.appointments_completed, 0) AS FLOAT) / ISNULL(appt.appointments_schedule, 0) * 100 
        END) +
        (CASE 
            WHEN ISNULL(vle.viral_load_eligible, 0) = 0 THEN 0 
            ELSE CAST(ISNULL(vlc.viral_load_samples, 0) AS FLOAT) / ISNULL(vle.viral_load_eligible, 0) * 100 
        END) +
        (CASE 
            WHEN ISNULL(vvl.viral_load_results, 0) = 0 THEN 0 
            ELSE CAST(ISNULL(svl.viral_load_suppressed, 0) AS FLOAT) / ISNULL(vvl.viral_load_results, 0) * 100 
        END) +
        (CASE
            WHEN ISNULL(tc.Tx_Cur, 0) = 0 THEN 0
            ELSE 100.0 - (CAST(ISNULL(iit.IIT, 0) AS DECIMAL(10, 2)) * 100.0 / ISNULL(tc.Tx_Cur, 0))
        END)
    ) / 4.0 AS final_score
FROM 
    cms.case_managers cm
LEFT JOIN Tx_Cur_CTE tc ON cm.id = tc.caseManagerId
LEFT JOIN IIT_CTE iit ON cm.id = iit.caseManagerId
LEFT JOIN Dead_CTE d ON cm.id = d.caseManagerId
LEFT JOIN Discontinued_CTE disc ON cm.id = disc.caseManagerId
LEFT JOIN TransferredOut_CTE tout ON cm.id = tout.caseManagerId
LEFT JOIN Appointments_CTE appt ON cm.id = appt.caseManagerId
LEFT JOIN AppointmentsKept_CTE ak ON cm.id = ak.caseManagerId
LEFT JOIN VLEligible_CTE vle ON cm.id = vle.caseManagerId
LEFT JOIN VLCollected_CTE vlc ON cm.id = vlc.caseManagerId
LEFT JOIN ValidVL_CTE vvl ON cm.id = vvl.caseManagerId
LEFT JOIN SuppressedVL_CTE svl ON cm.id = svl.caseManagerId;