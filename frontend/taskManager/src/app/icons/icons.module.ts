import { NgModule } from '@angular/core';

import { FeatherModule } from 'angular-feather';
import { Activity,
         Camera,
         CheckCircle,
         CheckSquare,
         Delete,
         Edit3,
         Github,
         Heart,
         LogIn,
         LogOut,
         Menu,
         Plus,
         PlusCircle,
         PlusSquare,
         Settings,
         Slash,
         Trash2,
         Triangle,
         User,
         UserCheck,
         UserPlus,
         XSquare

        } from 'angular-feather/icons';

const icons = {
  Activity,
  Camera,
  CheckCircle,
  CheckSquare,
  Delete,
  Edit3,
  Github,
  Heart,
  LogIn,
  LogOut,
  Menu,
  Plus,
  PlusCircle,
  PlusSquare,
  Settings,
  Slash,
  Trash2,
  Triangle,
  User,
  UserCheck,
  UserPlus,
  XSquare
};

@NgModule({
  declarations: [],
  imports: [
    FeatherModule.pick(icons)
  ],
  exports: [
    FeatherModule
  ],
})
export class IconsModule { }
