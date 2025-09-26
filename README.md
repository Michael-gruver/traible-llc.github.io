# Traible Frontend

A modern React application built with TypeScript, Vite, and Tailwind CSS.

## Features

- ⚡ **Vite** - Fast build tool and dev server
- ⚛️ **React 18** - Latest React with concurrent features
- 🔷 **TypeScript** - Type-safe development
- 🎨 **Tailwind CSS** - Utility-first CSS framework
- 🧪 **Vitest** - Fast unit testing
- 📦 **Drizzle ORM** - Type-safe database queries
- 🎯 **ESLint & Prettier** - Code quality and formatting

## Getting Started

### Prerequisites

- Node.js 18.18 or higher
- npm or yarn

### Installation

1. Clone the repository
2. Install dependencies:

   ```bash
   npm install
   ```

3. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

4. Update `.env` with your configuration

### Development

```bash
# Start development server
npm run dev

# Type checking
npm run typecheck

# Linting
npm run lint
npm run lint:fix

# Formatting
npm run format
npm run format:check

# Testing
npm run test
npm run test:ui
npm run test:coverage
```

### Database

```bash
# Generate migrations
npm run drizzle:generate

# Push schema changes
npm run drizzle:push

# Open Drizzle Studio
npm run drizzle:studio
```

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
├── client/                 # Frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/         # Route components
│   │   ├── hooks/         # Custom React hooks
│   │   ├── lib/           # Utility libraries
│   │   ├── store/         # State management
│   │   └── test/          # Test setup
│   └── index.html         # HTML entry point
├── shared/                # Shared types and schemas
├── migrations/            # Database migrations
└── dist/                  # Build output
```

## Tech Stack

- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **State Management**: Custom stores (Zustand-like)
- **Database**: PostgreSQL with Drizzle ORM
- **Testing**: Vitest, React Testing Library
- **Code Quality**: ESLint, Prettier
- **UI Components**: Radix UI primitives with custom styling

## Contributing

1. Follow the existing code style
2. Write tests for new features
3. Ensure all linting and type checks pass
4. Update documentation as needed

## License

MIT
