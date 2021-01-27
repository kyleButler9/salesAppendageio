sqlTempTableCreation = \
"""
CREATE TEMP TABLE fromSheet(
    org_name VARCHAR(255),
    complete Boolean);
"""
sqlUploadMany = \
"""
INSERT INTO fromSheet(org_name,complete)
VALUES(%s,%s);
"""
sqlUpsert = \
"""
LOCK TABLE orgs IN EXCLUSIVE MODE;

UPDATE orgs
SET complete = fromSheet.complete
FROM fromSheet
WHERE fromSheet.org_name = orgs.org_name;

INSERT INTO orgs(org_name,complete)
SELECT fromSheet.org_name, fromSheet.complete
FROM fromSheet
LEFT OUTER JOIN orgs ON (orgs.org_name = fromSheet.org_name)
WHERE orgs.org_name IS NULL;
"""
