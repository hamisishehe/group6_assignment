import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  imports: [FormsModule, CommonModule, HttpClientModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {


  loading: boolean = false;

  username: string = '';
  phone_number: string = '';
  email: string = '';
  password: string = '';
  message: string = '';

  constructor(private http: HttpClient, private router: Router) {}

  Register() {
    this.loading = true;

    console.log('loading');

    // Sanitize inputs
    const sanitizedEmail = this.sanitizeInput(this.email);
    const sanitizedPassword = this.sanitizeInput(this.password);

    // Basic validation
    if (!this.validateInputs(sanitizedEmail, sanitizedPassword)) {
      this.message = 'Invalid email or password format.';
      this.loading = false;
      return;
    }

    const LoginForm = {
      username:this.username,
      email: sanitizedEmail,
      phone_number:this.phone_number,
      password: sanitizedPassword,
    };

    this.http
      .post<any>(
        `http://localhost:5000/auth/register`, // Use baseUrl from environment
        LoginForm
      )
      .subscribe(
        (response) => {
            console.log('Registration successfully');
            this.message ="Registration Successfully";
            this.loading = false;
          },

        (error) => {
          this.message = 'Invalid Details';
          this.loading = false;
        }
      );
  }

  // Simple input sanitization
  private sanitizeInput(input: string): string {
    return input.trim(); // Trims whitespace
  }

  // Basic validation for email and password
  private validateInputs(email: string, password: string): boolean {
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/; // Simple email pattern
    return emailPattern.test(email) && password.length >= 6; // Password must be at least 6 characters
  }
}
