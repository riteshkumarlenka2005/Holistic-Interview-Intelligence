import { createContext, useContext } from 'react';
import { MemberContextType } from './types';

export const MemberContext = createContext<MemberContextType | undefined>(undefined);

export const useMember = () => {
  const context = useContext(MemberContext);
  if (context === undefined) {
    throw new Error('useMember must be used within a MemberProvider');
  }
  return context;
};
