/**
 * English (en) translation dictionary.
 *
 * This is the source of truth for all translation keys.
 * Other locale dictionaries must match this structure exactly.
 *
 * Key naming convention: feature.section.label
 * - feature: The domain/feature area (nav, dashboard, applications, etc.)
 * - section: Optional sub-grouping within the feature
 * - label: The specific string identifier
 *
 * Interpolation syntax: {paramName}
 * - Parameters are replaced at runtime with provided values
 * - All values are escaped (no HTML injection)
 */

export const en = {
    // ---------------------------------------------------------------------------
    // Common / Shared
    // ---------------------------------------------------------------------------
    common: {
        loading: "Loading...",
        error: "An error occurred",
        retry: "Retry",
        cancel: "Cancel",
        save: "Save",
        delete: "Delete",
        edit: "Edit",
        create: "Create",
        search: "Search",
        filter: "Filter",
        noResults: "No results found",
        viewAll: "View all",
        back: "Back",
        next: "Next",
        previous: "Previous",
        confirm: "Confirm",
        close: "Close",
    },

    // ---------------------------------------------------------------------------
    // Navigation
    // ---------------------------------------------------------------------------
    nav: {
        home: "Home",
        dashboard: "Dashboard",
        jobs: "Jobs",
        applications: "Applications",
        resumes: "Resumes",
        tools: "Tools",
        profile: "Profile",
        billing: "Billing",
        settings: "Settings",
        logout: "Log out",
        login: "Log in",
        signup: "Sign up",
    },

    // ---------------------------------------------------------------------------
    // Authentication
    // ---------------------------------------------------------------------------
    auth: {
        login: {
            title: "Welcome back",
            subtitle: "Sign in to your account",
            emailLabel: "Email address",
            emailPlaceholder: "you@example.com",
            passwordLabel: "Password",
            passwordPlaceholder: "Enter your password",
            submitButton: "Sign in",
            forgotPassword: "Forgot password?",
            noAccount: "Don't have an account?",
            signupLink: "Sign up",
        },
        signup: {
            title: "Create your account",
            subtitle: "Start your job search journey",
            nameLabel: "Full name",
            namePlaceholder: "John Doe",
            emailLabel: "Email address",
            emailPlaceholder: "you@example.com",
            passwordLabel: "Password",
            passwordPlaceholder: "Create a password",
            submitButton: "Create account",
            hasAccount: "Already have an account?",
            loginLink: "Sign in",
        },
        errors: {
            invalidCredentials: "Invalid email or password",
            emailRequired: "Email is required",
            passwordRequired: "Password is required",
            nameRequired: "Name is required",
            emailInvalid: "Please enter a valid email address",
            passwordTooShort: "Password must be at least 8 characters",
        },
    },

    // ---------------------------------------------------------------------------
    // Dashboard
    // ---------------------------------------------------------------------------
    dashboard: {
        welcome: "Welcome back",
        welcomeWithName: "Welcome back, {name}!",
        overview: "Here's an overview of your job search",
        stats: {
            jobsMatched: "Jobs Matched",
            applications: "Applications",
            submitted: "Submitted",
            pendingReview: "Pending Review",
        },
        recentApplications: {
            title: "Recent Applications",
            empty: "No applications yet",
        },
        topMatches: {
            title: "Top Job Matches",
            empty: "No jobs found",
            matchScore: "{score}% Match",
            noScore: "N/A",
        },
    },

    // ---------------------------------------------------------------------------
    // Applications / Kanban
    // ---------------------------------------------------------------------------
    applications: {
        title: "Applications",
        stages: {
            saved: "Saved",
            applied: "Applied",
            interviewing: "Interviewing",
            offer: "Offer",
            rejected: "Rejected",
        },
        status: {
            pendingReview: "Pending Review",
            approved: "Approved",
            submitted: "Submitted",
            failed: "Failed",
            manualNeeded: "Manual Action Needed",
        },
        card: {
            matchScore: "{score}% match",
            appliedOn: "Applied on {date}",
            addedOn: "Added on {date}",
        },
        detail: {
            notes: "Notes",
            timeline: "Timeline",
            addNote: "Add a note...",
            noNotes: "No notes yet",
        },
        actions: {
            moveToApplied: "Move to Applied",
            archive: "Archive",
            viewJob: "View Job",
        },
        proTips: {
            title: "Pro Tips",
            followUp: "Follow up on applications after 1 week",
            customize: "Customize your resume for each application",
            research: "Research the company before interviewing",
        },
    },

    // ---------------------------------------------------------------------------
    // Jobs
    // ---------------------------------------------------------------------------
    jobs: {
        title: "Job Matches",
        filters: {
            all: "All Jobs",
            remote: "Remote",
            hybrid: "Hybrid",
            onsite: "On-site",
        },
        card: {
            salary: "Salary",
            location: "Location",
            posted: "Posted {date}",
            matchScore: "{score}% Match",
        },
        actions: {
            apply: "Apply",
            save: "Save",
            dismiss: "Dismiss",
        },
        empty: {
            title: "No jobs found",
            description: "Try adjusting your filters or check back later",
        },
    },

    // ---------------------------------------------------------------------------
    // Resume Builder
    // ---------------------------------------------------------------------------
    resume: {
        title: "Resume Builder",
        templates: {
            title: "Choose a Template",
            professional: "Professional Modern",
            classic: "Classic Traditional",
            techMinimalist: "Tech Minimalist",
            twoColumn: "Two Column",
            atsOptimized: "ATS Optimized",
        },
        sections: {
            contact: "Contact Information",
            summary: "Professional Summary",
            experience: "Work Experience",
            education: "Education",
            skills: "Skills",
            projects: "Projects",
            certifications: "Certifications",
            awards: "Awards",
            languages: "Languages",
            custom: "Custom Sections",
        },
        actions: {
            preview: "Preview",
            download: "Download PDF",
            save: "Save Resume",
            aiAssist: "AI Assistant",
            share: "Share",
            export: "Export",
            import: "Import",
            undo: "Undo",
            redo: "Redo",
        },
        ai: {
            title: "AI Assistant",
            summary: "Generate Summary",
            skills: "Suggest Skills",
            atsCheck: "ATS Check",
            optimizing: "Optimizing...",
        },
        ats: {
            title: "ATS Score",
            subtitle: "Applicant Tracking System",
            excellent: "Excellent",
            veryGood: "Very Good",
            good: "Good",
            fair: "Fair",
            needsWork: "Needs Work",
            notCalculated: "Not Calculated",
            breakdown: "Score Breakdown",
            keywords: "Keywords",
            matched: "Matched",
            missing: "Missing",
            suggestions: "Suggestions",
            recalculate: "Recalculate Score",
            keywordMatch: "Keyword Match",
            formatting: "Formatting",
            sectionCompleteness: "Sections",
            quantifiedAchievements: "Achievements",
            length: "Length",
            contactInfo: "Contact Info",
        },
        settings: {
            title: "Template Settings",
            primaryColor: "Primary Color",
            fontFamily: "Font Family",
            fontSize: "Font Size",
            spacing: "Spacing",
            pageSize: "Page Size",
            reset: "Reset to Defaults",
            small: "Small",
            medium: "Medium",
            large: "Large",
            compact: "Compact",
            normal: "Normal",
            spacious: "Spacious",
            letter: "Letter",
            a4: "A4",
        },
        share: {
            title: "Share Resume",
            generateLink: "Generate Share Link",
            noLink: "No Share Link Yet",
            noLinkDescription: "Generate a link to share your resume with anyone",
            public: "Public",
            private: "Private",
            anyoneCanView: "Anyone with the link can view",
            linkDisabled: "Link is disabled",
            copyLink: "Copy Link",
            copied: "Copied!",
            openPreview: "Open Preview",
            removeLink: "Remove Link",
        },
        exportImport: {
            title: "Export / Import",
            exportTitle: "Export Resume",
            importTitle: "Import Resume",
            applybotsFormat: "ApplyBots Format",
            applybotsDescription: "Complete backup with all settings",
            jsonResumeFormat: "JSON Resume Format",
            jsonResumeDescription: "Standard format for other tools",
            importFromJson: "Import from JSON",
            importDescription: "Supports ApplyBots and JSON Resume formats",
            importSuccess: "Resume imported successfully!",
            importError: "Failed to import resume",
            localProcessing: "Your data is processed locally and not uploaded anywhere.",
        },
    },

    // ---------------------------------------------------------------------------
    // Profile
    // ---------------------------------------------------------------------------
    profile: {
        title: "Profile",
        greeting: "Hello, {name}!",
        sections: {
            personal: "Personal Information",
            preferences: "Job Preferences",
            notifications: "Notifications",
        },
        fields: {
            fullName: "Full Name",
            email: "Email",
            phone: "Phone",
            location: "Location",
            linkedin: "LinkedIn",
            portfolio: "Portfolio",
        },
    },

    // ---------------------------------------------------------------------------
    // Errors & Validation
    // ---------------------------------------------------------------------------
    errors: {
        generic: "Something went wrong. Please try again.",
        network: "Network error. Please check your connection.",
        notFound: "The requested resource was not found.",
        unauthorized: "You are not authorized to perform this action.",
        validation: {
            required: "{field} is required",
            invalid: "{field} is invalid",
            tooShort: "{field} is too short",
            tooLong: "{field} is too long",
        },
    },

    // ---------------------------------------------------------------------------
    // Accessibility
    // ---------------------------------------------------------------------------
    a11y: {
        skipToContent: "Skip to main content",
        closeMenu: "Close menu",
        openMenu: "Open menu",
        loading: "Loading content",
        expandSection: "Expand {section}",
        collapseSection: "Collapse {section}",
    },
} as const;

/**
 * Type representing the English dictionary structure.
 * Used for key derivation (TranslationKey type).
 */
export type EnDictionary = typeof en;

/**
 * Recursively converts all string literal types to `string`.
 * Used to create a structural type that enforces keys but allows different values.
 */
type DeepStringify<T> = T extends string
    ? string
    : T extends object
    ? { readonly [K in keyof T]: DeepStringify<T[K]> }
    : T;

/**
 * Structural type for locale dictionaries.
 * Enforces the same key structure as English but allows different string values.
 */
export type LocaleDictionary = DeepStringify<EnDictionary>;
