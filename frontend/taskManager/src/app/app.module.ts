import { NgModule, APP_INITIALIZER } from '@angular/core';
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
import { AuthService } from './services/auth.service';
import { RegisterComponent } from './components/register/register.component';
import { IconsModule } from './icons/icons.module';
import { NavbarComponent } from './components/navbar/navbar.component';
import { NewTaskModalComponent } from './components/todo/new-tasks-modal/new-tasks-modal.component';
import { EditTaskModalComponent } from './components/todo/edit-tasks-modal/edit-tasks-modal.component';

export function initializeAuth(authService: AuthService) {
  return (): Promise<void> => {
    return new Promise<void>((resolve) => {
      const token = authService.getToken();

      if (!token) {
        console.log('APP_INITIALIZER: No hay token');
        resolve();
        return;
      }

      console.log('APP_INITIALIZER: Token encontrado, verificando...');

      authService.getCurrentUser().subscribe({
        next: (user) => {
          console.log('APP_INITIALIZER: Usuario verificado exitosamente:', user.username);
          resolve();
        },
        error: (err) => {
          console.log('APP_INITIALIZER: Error al verificar token, limpiando sesión');
          authService.logout();
          resolve();
        }
      });

      setTimeout(() => {
        console.log('APP_INITIALIZER: Timeout, continuando...');
        resolve();
      }, 3000);
    });
  };
}


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
    },
    {
      provide: APP_INITIALIZER,
      useFactory: initializeAuth,
      deps: [AuthService],
      multi: true
    }
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
