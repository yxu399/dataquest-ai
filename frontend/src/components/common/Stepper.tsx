import React from 'react';

export interface StepperStep {
  id: string;
  name: string;
  status: 'complete' | 'current' | 'upcoming';
}

interface StepperProps {
  steps: StepperStep[];
}

export const Stepper: React.FC<StepperProps> = ({ steps }) => {
  return (
    <nav aria-label="Progress">
      <ol className="flex items-center">
        {steps.map((step, stepIdx) => (
          <li key={step.name} className={`${stepIdx !== steps.length - 1 ? 'pr-8 sm:pr-20' : ''} relative`}>
            {step.status === 'complete' ? (
              <>
                <div className="absolute inset-0 flex items-center" aria-hidden="true">
                  <div className="h-0.5 w-full bg-blue-600" />
                </div>
                <div className="relative w-8 h-8 flex items-center justify-center bg-blue-600 rounded-full">
                  <svg className="w-5 h-5 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>
              </>
            ) : step.status === 'current' ? (
              <>
                <div className="absolute inset-0 flex items-center" aria-hidden="true">
                  <div className="h-0.5 w-full bg-gray-200" />
                </div>
                <div className="relative w-8 h-8 flex items-center justify-center bg-white border-2 border-blue-600 rounded-full">
                  <span className="h-2.5 w-2.5 bg-blue-600 rounded-full" />
                </div>
              </>
            ) : (
              <>
                <div className="absolute inset-0 flex items-center" aria-hidden="true">
                  <div className="h-0.5 w-full bg-gray-200" />
                </div>
                <div className="w-8 h-8 flex items-center justify-center bg-white border-2 border-gray-300 rounded-full">
                  <span className="h-2.5 w-2.5 bg-gray-300 rounded-full" />
                </div>
              </>
            )}
            <span className="absolute top-10 left-1/2 transform -translate-x-1/2 text-xs font-medium text-gray-500">
              {step.name}
            </span>
          </li>
        ))}
      </ol>
    </nav>
  );
};