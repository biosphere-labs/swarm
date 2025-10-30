import { cn } from '@/lib/utils';

describe('cn utility', () => {
  it('merges class names correctly', () => {
    const result = cn('bg-red-500', 'text-white');
    expect(result).toBe('bg-red-500 text-white');
  });

  it('handles conditional classes', () => {
    const result = cn('base-class', true && 'conditional-class', false && 'not-included');
    expect(result).toBe('base-class conditional-class');
  });

  it('merges Tailwind classes correctly', () => {
    const result = cn('px-2 py-1', 'p-4');
    // p-4 should override px-2 py-1
    expect(result).toBe('p-4');
  });

  it('handles empty inputs', () => {
    const result = cn();
    expect(result).toBe('');
  });
});
