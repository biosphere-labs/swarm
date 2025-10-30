# Decomposition Pipeline Control Center - Frontend

A Next.js 14 application with App Router, TypeScript, Tailwind CSS, and shadcn/ui components for the LangGraph decomposition pipeline control center.

## Tech Stack

- **Framework:** Next.js 14 with App Router
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **UI Components:** shadcn/ui (built on Radix UI primitives)
- **Visualization:** ReactFlow, Recharts
- **Markdown:** react-markdown with remark-gfm
- **State Management:** Zustand
- **Testing:** Jest with React Testing Library

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the application.

### Build

```bash
npm run build
```

### Test

```bash
npm test
```

### Lint

```bash
npm run lint
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   └── globals.css        # Global styles with Tailwind
├── components/            # React components
│   └── ui/               # shadcn/ui components
│       ├── button.tsx
│       └── card.tsx
├── lib/                   # Utility functions
│   └── utils.ts          # cn() utility for class merging
├── __tests__/            # Jest tests
│   ├── Home.test.tsx
│   ├── Button.test.tsx
│   └── utils.test.ts
└── public/               # Static assets

```

## Features

- **Real-time Pipeline Monitoring:** Track decomposition pipeline progress
- **Interactive Visualizations:** Graph and tree views of problem decomposition
- **Agent Pool Monitoring:** View activity across specialized agent pools
- **Human-in-the-Loop Controls:** Approve, reject, or modify decisions at approval gates
- **Technique Catalog:** Browse algorithmic decomposition techniques
- **Export & Analysis:** Export results and view detailed metrics

## shadcn/ui Components

This project uses shadcn/ui for its component library. To add new components:

```bash
npx shadcn-ui@latest add <component-name>
```

For example:
```bash
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add dropdown-menu
```

## Environment Variables

Create a `.env.local` file for environment-specific configuration:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Integration

The frontend is designed to connect to a FastAPI backend running on port 8000. API routes should be created in `app/api/` for server-side operations.

## Testing

Tests are written using Jest and React Testing Library. Run tests with:

```bash
npm test           # Run all tests
npm run test:watch # Run tests in watch mode
```

## License

Private project - All rights reserved
