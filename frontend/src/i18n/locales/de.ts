/**
 * German (de) translation dictionary.
 *
 * Must match the structure of en.ts exactly.
 * Use LocaleDictionary type to ensure key structure compatibility.
 */

import type { LocaleDictionary } from "./en";

export const de: LocaleDictionary = {
  // ---------------------------------------------------------------------------
  // Common / Shared
  // ---------------------------------------------------------------------------
  common: {
    loading: "Wird geladen...",
    error: "Ein Fehler ist aufgetreten",
    retry: "Erneut versuchen",
    cancel: "Abbrechen",
    save: "Speichern",
    delete: "Löschen",
    edit: "Bearbeiten",
    create: "Erstellen",
    search: "Suchen",
    filter: "Filtern",
    noResults: "Keine Ergebnisse gefunden",
    viewAll: "Alle anzeigen",
    back: "Zurück",
    next: "Weiter",
    previous: "Zurück",
    confirm: "Bestätigen",
    close: "Schließen",
  },

  // ---------------------------------------------------------------------------
  // Navigation
  // ---------------------------------------------------------------------------
  nav: {
    home: "Startseite",
    dashboard: "Dashboard",
    jobs: "Jobs",
    applications: "Bewerbungen",
    resumes: "Lebensläufe",
    tools: "Tools",
    profile: "Profil",
    billing: "Abrechnung",
    settings: "Einstellungen",
    logout: "Abmelden",
    login: "Anmelden",
    signup: "Registrieren",
  },

  // ---------------------------------------------------------------------------
  // Authentication
  // ---------------------------------------------------------------------------
  auth: {
    login: {
      title: "Willkommen zurück",
      subtitle: "Melden Sie sich bei Ihrem Konto an",
      emailLabel: "E-Mail-Adresse",
      emailPlaceholder: "sie@beispiel.de",
      passwordLabel: "Passwort",
      passwordPlaceholder: "Passwort eingeben",
      submitButton: "Anmelden",
      forgotPassword: "Passwort vergessen?",
      noAccount: "Noch kein Konto?",
      signupLink: "Registrieren",
    },
    signup: {
      title: "Konto erstellen",
      subtitle: "Starten Sie Ihre Jobsuche",
      nameLabel: "Vollständiger Name",
      namePlaceholder: "Max Mustermann",
      emailLabel: "E-Mail-Adresse",
      emailPlaceholder: "sie@beispiel.de",
      passwordLabel: "Passwort",
      passwordPlaceholder: "Passwort erstellen",
      submitButton: "Konto erstellen",
      hasAccount: "Bereits ein Konto?",
      loginLink: "Anmelden",
    },
    errors: {
      invalidCredentials: "Ungültige E-Mail oder Passwort",
      emailRequired: "E-Mail ist erforderlich",
      passwordRequired: "Passwort ist erforderlich",
      nameRequired: "Name ist erforderlich",
      emailInvalid: "Bitte geben Sie eine gültige E-Mail-Adresse ein",
      passwordTooShort: "Passwort muss mindestens 8 Zeichen lang sein",
    },
  },

  // ---------------------------------------------------------------------------
  // Dashboard
  // ---------------------------------------------------------------------------
  dashboard: {
    welcome: "Willkommen zurück",
    welcomeWithName: "Willkommen zurück, {name}!",
    overview: "Hier ist eine Übersicht Ihrer Jobsuche",
    stats: {
      jobsMatched: "Passende Jobs",
      applications: "Bewerbungen",
      submitted: "Eingereicht",
      pendingReview: "Ausstehende Überprüfung",
    },
    recentApplications: {
      title: "Letzte Bewerbungen",
      empty: "Noch keine Bewerbungen",
    },
    topMatches: {
      title: "Top Job-Matches",
      empty: "Keine Jobs gefunden",
      matchScore: "{score}% Übereinstimmung",
      noScore: "K.A.",
    },
  },

  // ---------------------------------------------------------------------------
  // Applications / Kanban
  // ---------------------------------------------------------------------------
  applications: {
    title: "Bewerbungen",
    stages: {
      saved: "Gespeichert",
      applied: "Beworben",
      interviewing: "Im Gespräch",
      offer: "Angebot",
      rejected: "Abgelehnt",
    },
    status: {
      pendingReview: "Ausstehende Überprüfung",
      approved: "Genehmigt",
      submitted: "Eingereicht",
      failed: "Fehlgeschlagen",
      manualNeeded: "Manuelle Aktion erforderlich",
    },
    card: {
      matchScore: "{score}% Übereinstimmung",
      appliedOn: "Beworben am {date}",
      addedOn: "Hinzugefügt am {date}",
    },
    detail: {
      notes: "Notizen",
      timeline: "Zeitlinie",
      addNote: "Notiz hinzufügen...",
      noNotes: "Noch keine Notizen",
    },
    actions: {
      moveToApplied: "Zu Beworben verschieben",
      archive: "Archivieren",
      viewJob: "Job anzeigen",
    },
    proTips: {
      title: "Profi-Tipps",
      followUp: "Nachfassen nach 1 Woche",
      customize: "Lebenslauf für jede Bewerbung anpassen",
      research: "Unternehmen vor dem Gespräch recherchieren",
    },
  },

  // ---------------------------------------------------------------------------
  // Jobs
  // ---------------------------------------------------------------------------
  jobs: {
    title: "Job-Matches",
    filters: {
      all: "Alle Jobs",
      remote: "Remote",
      hybrid: "Hybrid",
      onsite: "Vor Ort",
    },
    card: {
      salary: "Gehalt",
      location: "Standort",
      posted: "Veröffentlicht {date}",
      matchScore: "{score}% Übereinstimmung",
    },
    actions: {
      apply: "Bewerben",
      save: "Speichern",
      dismiss: "Verwerfen",
    },
    empty: {
      title: "Keine Jobs gefunden",
      description: "Versuchen Sie, Ihre Filter anzupassen oder schauen Sie später wieder vorbei",
    },
  },

  // ---------------------------------------------------------------------------
  // Resume Builder
  // ---------------------------------------------------------------------------
  resume: {
    title: "Lebenslauf-Builder",
    templates: {
      title: "Vorlage auswählen",
      professional: "Professionell Modern",
      classic: "Klassisch Traditionell",
      techMinimalist: "Tech Minimalistisch",
      twoColumn: "Zwei Spalten",
      atsOptimized: "ATS-optimiert",
    },
    sections: {
      contact: "Kontaktinformationen",
      summary: "Berufliche Zusammenfassung",
      experience: "Berufserfahrung",
      education: "Ausbildung",
      skills: "Fähigkeiten",
      projects: "Projekte",
    },
    actions: {
      preview: "Vorschau",
      download: "PDF herunterladen",
      save: "Lebenslauf speichern",
      aiAssist: "KI-Assistent",
    },
    ai: {
      title: "KI-Assistent",
      summary: "Zusammenfassung generieren",
      skills: "Fähigkeiten vorschlagen",
      atsCheck: "ATS-Check",
      optimizing: "Optimiere...",
    },
  },

  // ---------------------------------------------------------------------------
  // Profile
  // ---------------------------------------------------------------------------
  profile: {
    title: "Profil",
    greeting: "Hallo, {name}!",
    sections: {
      personal: "Persönliche Informationen",
      preferences: "Job-Präferenzen",
      notifications: "Benachrichtigungen",
    },
    fields: {
      fullName: "Vollständiger Name",
      email: "E-Mail",
      phone: "Telefon",
      location: "Standort",
      linkedin: "LinkedIn",
      portfolio: "Portfolio",
    },
  },

  // ---------------------------------------------------------------------------
  // Errors & Validation
  // ---------------------------------------------------------------------------
  errors: {
    generic: "Etwas ist schief gelaufen. Bitte versuchen Sie es erneut.",
    network: "Netzwerkfehler. Bitte überprüfen Sie Ihre Verbindung.",
    notFound: "Die angeforderte Ressource wurde nicht gefunden.",
    unauthorized: "Sie sind nicht berechtigt, diese Aktion auszuführen.",
    validation: {
      required: "{field} ist erforderlich",
      invalid: "{field} ist ungültig",
      tooShort: "{field} ist zu kurz",
      tooLong: "{field} ist zu lang",
    },
  },

  // ---------------------------------------------------------------------------
  // Accessibility
  // ---------------------------------------------------------------------------
  a11y: {
    skipToContent: "Zum Hauptinhalt springen",
    closeMenu: "Menü schließen",
    openMenu: "Menü öffnen",
    loading: "Inhalt wird geladen",
    expandSection: "{section} erweitern",
    collapseSection: "{section} einklappen",
  },
} as const;
