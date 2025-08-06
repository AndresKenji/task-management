import { NgModule } from '@angular/core';

import { FeatherModule } from 'angular-feather';
import { Activity,
         BarChart,
         Camera,
         CheckCircle,
         CheckSquare,
         Delete,
         Edit3,
         Github,
         Globe,
         Heart,
         List,
         LogIn,
         LogOut,
         Menu,
         Plus,
         PlusCircle,
         PlusSquare,
         RefreshCw,
         Settings,
         Slash,
         Trash2,
         TrendingUp,
         Triangle,
         User,
         UserCheck,
         UserPlus,
         XSquare

        } from 'angular-feather/icons';

const icons = {
  Activity,
  BarChart,
  Camera,
  CheckCircle,
  CheckSquare,
  Delete,
  Edit3,
  Github,
  Globe,
  Heart,
  List,
  LogIn,
  LogOut,
  Menu,
  Plus,
  PlusCircle,
  PlusSquare,
  RefreshCw,
  Settings,
  Slash,
  Trash2,
  TrendingUp,
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
