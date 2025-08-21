# Requirements Document

## Introduction

Veritas is a decentralized freelancing platform designed as a mini-application within the WorldApp ecosystem. The platform connects global service providers and consumers through a trusted, verified marketplace that leverages World ID for user verification and USDC for seamless cross-border payments. The application emphasizes trust, low transaction fees, instant global payments, and a simplified user experience that abstracts blockchain complexity.

## Requirements

### Requirement 1: User Identity Verification

**User Story:** As a platform user, I want to be verified through World ID so that I can trust that all other users are unique, real humans.

#### Acceptance Criteria

1. WHEN a user first accesses the platform THEN the system SHALL require World ID verification before allowing any profile creation or service interaction
2. WHEN a user attempts to create a profile THEN the system SHALL verify their World ID status and store their unique worldId identifier
3. WHEN a user tries to perform sensitive actions (creating services, ordering services, leaving reviews) THEN the system SHALL validate their World ID verification status
4. IF a user is not verified THEN the system SHALL redirect them to the World ID verification process
5. WHEN verification is complete THEN the system SHALL store the verification status in global application state

### Requirement 2: User Profile Management

**User Story:** As a platform user, I want to create and manage my profile so that I can showcase my skills and build reputation on the platform.

#### Acceptance Criteria

1. WHEN a verified user creates a profile THEN the system SHALL store their displayName, bio (max 500 characters), location, skills, and provider status
2. WHEN a user updates their profile THEN the system SHALL validate the input data and persist changes to the backend
3. WHEN viewing a profile THEN the system SHALL display the user's reputation including average rating and completed jobs count
4. WHEN a user marks themselves as a service provider THEN the system SHALL enable service creation functionality for that user
5. IF a user has not completed World ID verification THEN the system SHALL prevent profile creation

### Requirement 3: Service Marketplace

**User Story:** As a service provider, I want to create and list my services so that potential clients can discover and purchase them.

#### Acceptance Criteria

1. WHEN a verified provider creates a service THEN the system SHALL store the service with title, description, category, price in USDC, and creation timestamp
2. WHEN users browse services THEN the system SHALL display services with pagination and category filtering
3. WHEN a user searches for services THEN the system SHALL return relevant results based on title, description, and category
4. WHEN viewing service details THEN the system SHALL display provider information, service description, price, and provider ratings
5. WHEN a service is created THEN the system SHALL assign a unique serviceId and associate it with the provider's worldId

### Requirement 4: Job Order and Escrow System

**User Story:** As a service consumer, I want to order services with secure payment handling so that my funds are protected until work is completed satisfactorily.

#### Acceptance Criteria

1. WHEN a consumer orders a service THEN the system SHALL create a job record with pending status and deploy an escrow smart contract
2. WHEN payment is initiated THEN the system SHALL use MiniKit to process USDC payment to the escrow contract
3. WHEN a job is accepted by the provider THEN the system SHALL update job status to "accepted" and notify both parties
4. WHEN work is completed THEN the provider SHALL mark the job as "in_review" for consumer approval
5. WHEN a consumer approves completed work THEN the system SHALL release funds from escrow to the provider
6. IF there is a dispute THEN the system SHALL maintain job status as "disputed" for future arbitration

### Requirement 5: Job Status Tracking

**User Story:** As a platform user, I want to track the progress of my jobs so that I know the current status of my orders and services.

#### Acceptance Criteria

1. WHEN a job is created THEN the system SHALL initialize status as "pending"
2. WHEN job status changes THEN the system SHALL update the job record with new status and timestamp
3. WHEN users view their dashboard THEN the system SHALL display all their jobs (as consumer and provider) with current status
4. WHEN a job reaches "completed" status THEN the system SHALL record completion timestamp
5. WHEN viewing job details THEN the system SHALL show status progression and relevant timestamps

### Requirement 6: Review and Reputation System

**User Story:** As a platform user, I want to leave and view reviews so that I can make informed decisions and build trust in the marketplace.

#### Acceptance Criteria

1. WHEN a job is completed THEN both consumer and provider SHALL be able to leave reviews for each other
2. WHEN submitting a review THEN the system SHALL require a rating (1-5) and optional comment
3. WHEN a review is submitted THEN the system SHALL update the reviewee's reputation metrics
4. WHEN viewing a user profile THEN the system SHALL display their average rating and recent reviews
5. WHEN calculating reputation THEN the system SHALL update average rating and completed jobs count in real-time

### Requirement 7: USDC Payment Integration

**User Story:** As a platform user, I want to make and receive payments in USDC so that I can transact globally with minimal fees and instant settlement.

#### Acceptance Criteria

1. WHEN a consumer orders a service THEN the system SHALL initiate USDC payment through MiniKit to the escrow contract
2. WHEN payment is successful THEN the system SHALL confirm job creation and notify the provider
3. WHEN work is approved THEN the system SHALL release USDC from escrow to the provider's wallet
4. WHEN displaying prices THEN the system SHALL show all amounts in USDC with appropriate decimal precision
5. IF payment fails THEN the system SHALL cancel the job order and notify the consumer

### Requirement 8: Smart Contract Escrow

**User Story:** As a platform user, I want my payments to be held in escrow so that funds are secure and released only when work is completed satisfactorily.

#### Acceptance Criteria

1. WHEN a job is created THEN the system SHALL deploy an escrow smart contract with consumer, provider, amount, and USDC token address
2. WHEN funds are deposited THEN the contract SHALL set status to "Funded"
3. WHEN consumer approves work THEN the contract SHALL allow releaseFunds() function to transfer USDC to provider
4. WHEN there is a dispute THEN the contract SHALL support refundFunds() functionality
5. WHEN contract is deployed THEN the system SHALL store the contract address in the job record

### Requirement 9: User Dashboard

**User Story:** As a platform user, I want a dashboard to manage my activities so that I can track my orders, services, and earnings in one place.

#### Acceptance Criteria

1. WHEN accessing the dashboard THEN the system SHALL display separate sections for jobs as consumer and as provider
2. WHEN viewing active jobs THEN the system SHALL show current status and next required actions
3. WHEN viewing completed jobs THEN the system SHALL display earnings, payments, and review status
4. WHEN managing services THEN providers SHALL be able to view, edit, and create new service listings
5. WHEN viewing statistics THEN the system SHALL show total earnings, completed jobs, and current reputation

### Requirement 10: Search and Discovery

**User Story:** As a service consumer, I want to search and filter services so that I can find providers that match my specific needs.

#### Acceptance Criteria

1. WHEN using the search bar THEN the system SHALL search across service titles, descriptions, and categories
2. WHEN applying category filters THEN the system SHALL display only services matching the selected categories
3. WHEN browsing the homepage THEN the system SHALL display featured services and popular categories
4. WHEN viewing search results THEN the system SHALL show service cards with key information and provider ratings
5. WHEN no results are found THEN the system SHALL display appropriate messaging and suggestions