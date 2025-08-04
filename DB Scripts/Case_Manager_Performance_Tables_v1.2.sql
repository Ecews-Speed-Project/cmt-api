-- Create Case Manager Performance Table
-- Drop table if it exists (optional - remove if you want to preserve existing data)
IF OBJECT_ID('cms.performance', 'U') IS NOT NULL
    DROP TABLE cms.performance;

-- Create the performance table
CREATE TABLE cms.performance (
    CaseManagerID VARCHAR(50) PRIMARY KEY,
    Tx_Cur INT DEFAULT 0,
    IIT INT DEFAULT 0,
    Dead INT DEFAULT 0,
    Discontinued INT DEFAULT 0,
    Transferred_Out INT DEFAULT 0,
    appointments_schedule INT DEFAULT 0,
    appointments_completed INT DEFAULT 0,
    appointment_compliance DECIMAL(5,2) DEFAULT 0,
    viral_load_eligible INT DEFAULT 0,
    viral_load_samples INT DEFAULT 0,
    sample_collection_rate DECIMAL(5,2) DEFAULT 0,
    viral_load_results INT DEFAULT 0,
    viral_load_suppressed INT DEFAULT 0,
    suppression_rate DECIMAL(5,2) DEFAULT 0,
	final_score DECIMAL(5,2) DEFAULT 0,
    created_date DATETIME2 DEFAULT GETDATE(),
    updated_date DATETIME2 DEFAULT GETDATE()
);


-- Optional: Create an index for better query performance
CREATE INDEX IX_performance_CaseManagerID ON cms.performance(CaseManagerID);

--============================================================================================
-- Create All Case Manager Performance Table
-- Drop table if it exists (optional - remove if you want to preserve existing data)
IF OBJECT_ID('cms.all_performance', 'U') IS NOT NULL
    DROP TABLE cms.all_performance;

-- Create the all performance table
CREATE TABLE cms.all_performance (
    id INT IDENTITY(1,1) PRIMARY KEY,
    CaseManagerID VARCHAR(50) NOT NULL,
    Tx_Cur INT DEFAULT 0,
    IIT INT DEFAULT 0,
    Dead INT DEFAULT 0,
    Discontinued INT DEFAULT 0,
    Transferred_Out INT DEFAULT 0,
    appointments_schedule INT DEFAULT 0,
    appointments_completed INT DEFAULT 0,
    appointment_compliance DECIMAL(5,2) DEFAULT 0,
    viral_load_eligible INT DEFAULT 0,
    viral_load_samples INT DEFAULT 0,
    sample_collection_rate DECIMAL(5,2) DEFAULT 0,
    viral_load_results INT DEFAULT 0,
    viral_load_suppressed INT DEFAULT 0,
    suppression_rate DECIMAL(5,2) DEFAULT 0,
	final_score DECIMAL(5,2) DEFAULT 0,
    created_date DATETIME2 DEFAULT GETDATE(),
    updated_date DATETIME2 DEFAULT GETDATE()
);


-- Optional: Create an index for better query performance
CREATE INDEX IX_all_performance_CaseManagerID ON cms.all_performance(CaseManagerID);