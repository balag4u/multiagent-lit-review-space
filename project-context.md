# Project Context

## Tech Stack
- **Framework**: Next.js (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI / Shadcn/ui
- **Icons**: Lucide React
- **State Management**: React Hooks (useState, useReducer, useContext) / TanStack Query (optional)
- **Package Manager**: npm

## Project Structure
```text
/
├── src/
│   ├── app/            # Next.js App Router (Routes, Layouts, API Handlers)
│   ├── components/     # React Components
│   │   ├── ui/         # Base UI primitives (shadcn)
│   │   └── ...         # Feature-specific components
│   ├── hooks/          # Custom React hooks
│   ├── lib/            # Shared utilities, constants, and config (e.g., utils.ts)
│   ├── services/       # External API integrations and data fetching logic
│   └── types/          # Global TypeScript type definitions
├── public/             # Static assets (images, fonts)
├── tailwind.config.ts  # Tailwind CSS configuration
└── tsconfig.json       # TypeScript configuration
```

## Coding Style & Conventions
- **Components**: 
  - Use Functional Components with arrow function syntax.
  - Prefer PascalCase for component filenames and definitions.
  - Use `lucide-react` for all iconography.
- **TypeScript**:
  - Explicitly type props and function returns.
  - Prefer `interface` for object structures and `type` for unions/primitives.
  - Avoid using `any`; use `unknown` or specific generics if necessary.
- **Naming**:
  - Variables/Functions: `camelCase`.
  - Constants: `UPPER_SNAKE_CASE`.
  - Folders: `kebab-case`.
- **Imports**:
  - Use absolute paths with the `@/` alias (e.g., `@/components/ui/button`).
  - Group imports: React/Next first, then external libs, then internal modules.

## Key Architecture Decisions
- **Server Components**: Default to React Server Components (RSC) for data fetching and static rendering.
- **Client Components**: Use `'use client'` only for interactive elements, event listeners, or browser-only APIs.
- **Styling**: Utility-first CSS via Tailwind. Use the `cn()` utility for conditional class merging.
- **Data Fetching**: Use Server Actions for mutations and standard `fetch` within RSCs for data retrieval.

## Common Commands
- `npm run dev`: Start the local development server.
- `npm run build`: Build the application for production.
- `npm run start`: Start the production server.
- `npm run lint`: Run ESLint for code quality checks.
- `npm run type-check`: Run TypeScript compiler to check for type errors.