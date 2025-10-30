import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Dashboard - Decomposition Pipeline',
  description: 'Real-time control center for LangGraph decomposition pipeline',
}

export default function Layout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return children
}
