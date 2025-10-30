import { render, screen } from '@testing-library/react';
import Home from '@/app/page';

describe('Home', () => {
  it('renders the main heading', () => {
    render(<Home />);
    const heading = screen.getByText(/Decomposition Pipeline Control Center/i);
    expect(heading).toBeInTheDocument();
  });

  it('renders feature cards', () => {
    render(<Home />);
    expect(screen.getByText('Pipeline Status')).toBeInTheDocument();
    expect(screen.getByText('Decomposition View')).toBeInTheDocument();
    expect(screen.getByText('Agent Pools')).toBeInTheDocument();
    expect(screen.getByText('Human Review')).toBeInTheDocument();
    expect(screen.getByText('Technique Catalog')).toBeInTheDocument();
    expect(screen.getByText('Export & Analysis')).toBeInTheDocument();
  });

  it('renders the subtitle', () => {
    render(<Home />);
    const subtitle = screen.getByText(/Real-time control center for the LangGraph decomposition pipeline/i);
    expect(subtitle).toBeInTheDocument();
  });
});
