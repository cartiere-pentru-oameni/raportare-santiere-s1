# Intro
This is a small web application that allows various citizens to report construction sites that do not have paperworks or that have other building permit regulations (ex: not respecting the number of floors, height, green space, number of parking spots, building setbacks, etc.). 
It was developed by "Cartiere pentru Oameni", and NGO from Romania that promotes transparency and citizen participation in urban development processes. Our area of interest is Sector 1, Bucharest, Romania.
If you want to learn more about us, please visit: https://cartierepentruoameni.ro/
If you want to use this application, please feel free to fork-it or to contact us for collaboration.

# Stakeholders
- Citizens: They can report construction sites that are not compliant with regulations.
- Validator: Trusted persons that can check if the reports are valid or not, and trigger further actions (ex: alerting authorities).
- Administrators: They manage the validator users and the overall system.

# User Stories

## Citizen Stories
- **CITIZEN-1**: As a citizen, I want to report a construction site that is not compliant with regulations so that authorities can take action.
- **CITIZEN-2**: As a citizen, I want to be able to check the paperworks before reporting a construction site, so I expect to have a tutorial available on how to do that.
- **CITIZEN-3**: As a citizen, I want to be able to choose on a map the location of the construction site I am reporting, so that the authorities can easily find it.
- **CITIZEN-4**: As a citizen, I want to be able to upload pictures of the construction site, so that the authorities can have evidence of the violation.
- **CITIZEN-5**: As a citizen, I want to input a type of violation (ex: no paperwork, noise violation, safety violation), so that the authorities can categorize the report.
- **CITIZEN-6**: As a citizen, I want to input an optional address, description, and other details about the construction site, so that the authorities have more context about the report.
- **CITIZEN-7**: As a citizen, I expect all reports to be publicly visible, and to see the status of each report (ex: pending, validated, resolved), so that I can stay informed about the situation.
- **CITIZEN-8**: As a citizen, I expect full anonimity when reporting a construction site, so that I feel safe and protected. No data should be collected that can identify me.
- **CITIZEN-9**: As a citizen, I want to be protected from other citizens that may write innapropriate reports, so I want to see only the map location, type of violation without description of pictures till the status is changed to "in-review".
- **CITIZEN-10**: As a citizen, I want to have a permanent link to each report, so I can easily save and share them with others.
- **CITIZEN-11**: As a citizen, I want to be protected from being discovered as a reporter by the exiff data in the pictures I upload, so I expect the platform to automatically strip exiff data from pictures.
- **CITIZEN-12**: As a citizen, I want to have statistics about the reports (including how many reports were deleted after 30 days because the validators did not take action), so that I can understand the effectiveness of the system.
- **CITIZEN-13**: As a citizen, I want to have an info page where I can get more information about the project, my rights, complete anonimity statement and contact details in case I have questions.
- **CITIZEN-14**: As a citizen, I want to have an anonymous contact form so I can report personal data on a report or other issues regarding the platform, so that I can communicate with the administrators without revealing my identity.

## Validator Stories
- **VALIDATOR-1**: As a validator, I want to log-in to the system using my credentials and be able to see all pending reports, so that I can validate or invalidate them.
- **VALIDATOR-2**: As a validator, I need to input comments that will be visible to the public when I invalidate a report, so that citizens understand why a report was invalidated. (ex: paperworks exists)
- **VALIDATOR-3**: As a validator, I want to input comments that will be visible to the public when I validate a report, so that citizens understand the next steps. (ex: authorities have been alerted)
- **VALIDATOR-4**: As a validator, I want to change the status of a report (pending -> validated -> waiting for authorities feedback -> resolved), so that citizens can stay informed about the situation.
- **VALIDATOR-5**: As a validator, I want to mark a report that contains inappropriate content (ex: offensive language, personal attacks), so that the system remains respectful and safe for all users.
- **VALIDATOR-6**: As a validator, In case I observe that the report contains personal data (names, phone numbers, address, pictures with faces of the reporter), I want to be able to remove that personal data from the report before validating it, so that the reporter remains anonymous. For the invalidated reports, the status should be changed to "invalidated".

## Administrator Stories
- **ADMIN-1**: As an administrator, I want to log-in to the system using my credentials
- **ADMIN-2**: As an administrator, I want to manage the list of users and their roles (validators, other admins), so that I can ensure the right people have access to the system.
- **ADMIN-3**: As an administrator, I want all reports that are "pending" after 30 days to be automatically deleted, in order to protect the citizen GDPR rights in case if a report contains personal data.

# Status flows
- Report is created with status "pending".
- Validator checks the report and decides if it's safe for public viewing. The status changes to "in-review" if it's ok and "not-allowed" if it contains inappropriate content.
- Validator can change status from "pending" to "validated" or "invalidated".
- If "validated", validator can change status to "waiting for authorities feedback".
- If "waiting for authorities feedback", validator can change status to "resolved". 

# Report types
- No paperwork
- Noise violation
- Pollution violation
- Others
#todo: expand this list

# Features
## Citizen features
1. Pictures upload with exiff data stripping
2. Map with location picker
3. Report form for with: 
    - Type of violation (dropdown)
    - Map location picker
    - Pictures upload
    - Optional address
    - Optional description
4. Map with all the reports, where I can click on each report to see details
5. Report viewer
    - With permanent link
    - Where I can see all the details that were validated to be safe for public viewing
6. Tutorial on how to check paperworks
7. Statistics page: 
    - Total number of reports
    - Number of reports by type
    - Number of reports by status
    - Completion time statistics
    - Number of reports deleted after 30 days
    - TODO: other useful statistics should be defined. 

## Validator and administrator features
1. Login system

## Validator features
1. Reports list with filters (by status, by type, by date)
2. Report review page where I can:
    - See all report details
    - Validate or invalidate the report
    - Input comments for validated or invalidated reports
    - Change report status
    - Remove personal data from the report if needed (modify text, remove pictures)
3. Mark report as inappropriate content

## Administrator features
1. User management page where I can:
    - Add/remove users
    - Assign roles to users (validator, administrator)
