import { NgModule } from '@angular/core';

import { FeatherModule } from 'angular-feather';
import { Activity,
         AlertTriangle,
         Award,
         BarChart,
         Camera,
         CheckCircle,
         CheckSquare,
         Clock,
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
         Smile,
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
  AlertTriangle,
  Award,
  BarChart,
  Camera,
  CheckCircle,
  CheckSquare,
  Clock,
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
  Smile,
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
