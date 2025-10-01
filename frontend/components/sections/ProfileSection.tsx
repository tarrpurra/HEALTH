import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Edit, Check, X } from "lucide-react";
import { User } from "../../lib/types";

interface ProfileSectionProps {
  currentUser: User | null;
  isEditing: boolean;
  editedName: string;
  setEditedName: (name: string) => void;
  editedAge: string;
  setEditedAge: (age: string) => void;
  editedGender: string;
  setEditedGender: (gender: string) => void;
  handleEdit: () => void;
  handleSave: () => void;
  handleCancel: () => void;
  isLoading: boolean;
}

export const ProfileSection: React.FC<ProfileSectionProps> = ({
  currentUser,
  isEditing,
  editedName,
  setEditedName,
  editedAge,
  setEditedAge,
  editedGender,
  setEditedGender,
  handleEdit,
  handleSave,
  handleCancel,
  isLoading,
}) => {
  return (
    <div className="flex items-center justify-center min-h-[calc(100vh-200px)] p-6">
      <Card className="max-w-2xl w-full">
        <CardHeader>
          <CardTitle>Profile Settings</CardTitle>
          <CardDescription>
            Manage your personal information
          </CardDescription>
        </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="text-sm font-medium">Name</label>
          <Input
            value={isEditing ? editedName : (currentUser?.name || "")}
            onChange={(e) => setEditedName(e.target.value)}
            className="mt-1"
            readOnly={!isEditing}
            placeholder={!isEditing ? "No name provided" : "Enter your name"}
          />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Age</label>
            <Input
              type="number"
              min="13"
              max="25"
              value={isEditing ? editedAge : (currentUser?.age?.toString() || "")}
              onChange={(e) => setEditedAge(e.target.value)}
              className="mt-1"
              readOnly={!isEditing}
              placeholder={!isEditing ? "No age provided" : "Enter your age"}
            />
          </div>
          <div>
            <label className="text-sm font-medium">Gender</label>
            {isEditing ? (
              <Select
                value={editedGender}
                onValueChange={setEditedGender}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue placeholder="Select gender" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="non-binary">Non-binary</SelectItem>
                  <SelectItem value="prefer-not-to-say">
                    Prefer not to say
                  </SelectItem>
                </SelectContent>
              </Select>
            ) : (
              <Input
                value={currentUser?.gender || ""}
                className="mt-1"
                readOnly
                placeholder="No gender provided"
              />
            )}
          </div>
        </div>
        <div>
          <label className="text-sm font-medium">Email</label>
          <Input
            value={currentUser?.email || ""}
            className="mt-1"
            readOnly
            placeholder="No email provided"
          />
        </div>
        {!isEditing ? (
          <Button onClick={handleEdit} className="w-full">
            <Edit className="h-4 w-4 mr-2" />
            Edit Profile
          </Button>
        ) : (
          <div className="flex gap-2">
            <Button
              onClick={handleSave}
              className="flex-1"
              disabled={isLoading}
            >
              <Check className="h-4 w-4 mr-2" />
              {isLoading ? "Saving..." : "Confirm"}
            </Button>
            <Button
              onClick={handleCancel}
              variant="outline"
              className="flex-1"
              disabled={isLoading}
            >
              <X className="h-4 w-4 mr-2" />
              Cancel
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
    </div>
  );
};
