import { Component } from '@angular/core';
import { UserDetails } from '../models/UserModel';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-header',
  imports: [],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent {


    userData: UserDetails | null = null;

  constructor(private http: HttpClient) {}

  ngOnInit() {
    this.getProfile();
  }

  logout() {
    localStorage.removeItem('token');
    window.location.href = '/auth/login';
  }

  getProfile() {
    const token = localStorage.getItem('token');

    if (token) {
      const headers = new HttpHeaders({
        Authorization: `Bearer ${token}`,
      });

      // Make the HTTP GET request to fetch the profile
      this.http
        .get<UserDetails>(`http://localhost:5000/user/profile`, {
          headers,
        }) // Use baseUrl here
        .subscribe(
          (data) => {
            this.userData = data;
            console.log(this.userData.username);
          },
          (error) => {
            console.error('Error fetching user profile', error);
          }
        );
    } else {
      console.error('No token found');
    }
  }
}
