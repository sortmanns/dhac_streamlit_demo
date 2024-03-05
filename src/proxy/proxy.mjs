import { initializeAuthProxy } from '@propelauth/auth-proxy'

// Replace with your configuration
await initializeAuthProxy({
    authUrl: "https://560282212.propelauthtest.com",
    integrationApiKey: "e5db4c793b13faf8ae7a1c2b337722bfc63e1e8521c6cd6f2782fb709ec868846e401c688bf3cc07f4881b14eb684ad4",
    proxyPort: 8000,
    urlWhereYourProxyIsRunning: 'http://localhost:8000',
    target: {
        host: 'localhost',
        port: 8501,
        protocol: 'http:'
    },
})
