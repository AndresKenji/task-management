import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { CommonModule } from '@angular/common';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TodoComponent } from './components/todo/todo.component';
import { LoginComponent } from './components/login/login.component';
import { ProfileComponent } from './components/profile/profile.component';
import { TaskStatsComponent } from './components/task-stats/task-stats.component';
import { AuthInterceptor } from './interceptors/auth.interceptor';
import { RegisterComponent } from './components/register/register.component';
import { IconsModule } from './icons/icons.module';
import { NavbarComponent } from './components/navbar/navbar.component';
import { NewTaskModalComponent } from './components/todo/new-tasks-modal/new-tasks-modal.component';
import { EditTaskModalComponent } from './components/todo/edit-tasks-modal/edit-tasks-modal.component';


@NgModule({
  declarations: [
    AppComponent,
    TodoComponent,
    LoginComponent,
    ProfileComponent,
    TaskStatsComponent,
    RegisterComponent,
    NavbarComponent,
    NewTaskModalComponent,
    EditTaskModalComponent,
  ],
  imports: [
    BrowserModule,
    CommonModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    IconsModule,
    ReactiveFormsModule,
  ],
  providers: [
    {
      provide: HTTP_INTERCEPTORS,
      useClass: AuthInterceptor,
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
