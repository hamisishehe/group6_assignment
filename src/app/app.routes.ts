import { authGuardGuard } from './auth/guard.guard';
import { CertificatesComponent } from './user/certificates/certificates.component';
import { DashboardComponent } from './user/dashboard/dashboard.component';
import { DomainComponent } from './user/domain/domain.component';
import { Routes } from '@angular/router';
import { WebsitesComponent } from './user/websites/websites.component';
import { MonitorComponent } from './user/monitor/monitor.component';
import { ProfileComponent } from './user/profile/profile.component';
import { LoginComponent } from './auth/login/login.component';
import { RegisterComponent } from './auth/register/register.component';
import { LayoutComponentb } from './user/layout/layout.component';

export const routes: Routes = [

  { path: 'auth/login', component: LoginComponent },
  { path: 'auth/register', component: RegisterComponent },

    //routes
  {
    path: '',
    component: LayoutComponentb,
    canActivate: [authGuardGuard],
    children: [
      {
        path: 'user/dashboard',
        component: DashboardComponent,
        canActivate: [authGuardGuard],
      },

      {
        path: 'user/domains_check',
        component: DomainComponent,
        canActivate: [authGuardGuard],
      },

      {
        path: 'user/certificates',
        component: CertificatesComponent,
        canActivate: [authGuardGuard],
      },

        {
        path: 'user/websites',
        component: WebsitesComponent,
        canActivate: [authGuardGuard],
      },
        {
        path: 'user/monitor',
        component: MonitorComponent,
        canActivate: [authGuardGuard],
      },

      {
        path: 'user/profile',
        component: ProfileComponent,
        canActivate: [authGuardGuard],
      },

    ],
  },
  //end admin router

  // Default redirect for empty path
  { path: '', redirectTo: '/auth/login', pathMatch: 'full' },

  // Wildcard route for 404
  { path: '**', redirectTo: '/notfound' },
];
