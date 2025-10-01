import { useState } from "react";
import { Button } from "@/components/ui/button";
import { ExerciseCard } from "../ExerciseCard";
import { Activity } from "lucide-react";
import { Exercise, ViewType } from "../../lib/types";
import allExercises from "../../lib/exercises.json";

interface ResourcesSectionProps {
  isLoadingExercises: boolean;
  suggestedExercises: Exercise[];
  setSelectedExercise: (exercise: Exercise | null) => void;
  setCurrentView: (view: ViewType) => void;
}

export const ResourcesSection: React.FC<ResourcesSectionProps> = ({
  isLoadingExercises,
  suggestedExercises,
  setSelectedExercise,
  setCurrentView,
}) => {
  const [showAllExercises, setShowAllExercises] = useState(false);

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-foreground mb-4">Your Suggested Exercises</h2>
        {isLoadingExercises ? (
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            <p className="mt-2 text-sm text-muted-foreground">Loading exercises...</p>
          </div>
        ) : suggestedExercises.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {suggestedExercises.map(exercise => (
              <ExerciseCard 
                key={exercise.id} 
                exercise={exercise} 
                onGetStarted={() => setSelectedExercise(exercise)} 
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 border rounded-lg">
            <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">
              Your AI mentor will add personalized exercises here after your sessions.
            </p>
            <Button
              onClick={() => setCurrentView("session")}
              className="mt-4"
              size="sm"
            >
              Start a Session to Get Started
            </Button>
          </div>
        )}
      </div>

      <div className="text-center">
        <Button onClick={() => setShowAllExercises(!showAllExercises)}>
          {showAllExercises ? "Less Exercises" : "More Exercises"}
        </Button>
      </div>

      {showAllExercises && (
        <div>
          <h2 className="text-2xl font-bold text-foreground mb-4 mt-8">All Available Exercises</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {allExercises.map(exercise => (
              <ExerciseCard 
                key={exercise.id} 
                exercise={exercise} 
                onGetStarted={() => setSelectedExercise(exercise)} 
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
