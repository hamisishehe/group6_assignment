import { Component, OnInit } from '@angular/core';
import { DataTable } from 'simple-datatables';
import { UserDetails } from '../models/UserModel';
import { WebsiteData } from '../models/WebsiteModels';
import { HttpClient, HttpHeaders, HttpClientModule } from '@angular/common/http';
import Swal from 'sweetalert2';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-websites',
  imports: [HttpClientModule,CommonModule,FormsModule],
  templateUrl: './websites.component.html',
  styleUrl: './websites.component.css'
})
export class WebsitesComponent implements OnInit{

       isOpen = false;
    isUploadOpen=false;
    isLoading: boolean = true;

  isUpdateModalOpen = false;
  selectedStudent: any = {};  // will store student info for editing


    userData : UserDetails | null = null;
    websites: WebsiteData [] = [];

    url : string='';
    name : string='';

    constructor(private http : HttpClient ){

    }


    ngOnInit() {

      setTimeout(() => {
        this.isLoading = false;
      }, 100);

      this.getProfile();
      this.GetWebsites();


    }


    getProfile() {
      const token = localStorage.getItem('token');

      if (token) {
        // Set the Authorization header with the Bearer token
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

              this.userData = data;

              console.log(this.userData.id);


            },
            (error) => {
              console.error('Error fetching user profile', error);
            }
          );
      } else {
        console.error('No token found');
      }
    }

   Insert_Website() {
  console.log("................");

  const form_data = {
    name: this.name,
    url: this.url,
  };

  console.log(form_data);

  const token = localStorage.getItem('token'); // Retrieve token

  if (token) {
    const headers = new HttpHeaders({
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`, // Add token here
    });

    this.http.post(`http://localhost:5000/target`, form_data, { headers })
      .subscribe(
        response => {
          Swal.fire({
            icon: 'success',
            title: 'New Website Successfully Added',
            showConfirmButton: false,
            timer: 1500,
          });

          window.location.reload();
        },
        error => {
          Swal.fire({
            icon: "error",
            title: "Oops...",
            text: error?.error?.message || "Something went wrong.",
            timer: 1500,
          });
        }
      );
  } else {
    Swal.fire({
      icon: "error",
      title: "Unauthorized",
      text: "No token found. Please log in.",
      timer: 1500,
    });
  }
}





GetWebsites() {
  console.log("................");

  const token = localStorage.getItem('token');

  if (token) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<WebsiteData[]>(`http://localhost:5000/target`, { headers })
      .subscribe(
        response => {
          this.websites = response;
          console.log(this.websites);
          this.initializeTable();
        },
        error => {
          console.error('Error fetching websites:', error);
        }
      );
  } else {
    console.error('No token found. Cannot fetch websites.');
  }
}


    openModal() {
      this.isOpen = true;
    }

    closeModal() {
      this.isOpen = false;
    }




    initializeTable(): void {
      setTimeout(() => {
        let datatable = new DataTable('#search-table');
        console.log('Table initialized');
      }, 100);
    }
}
