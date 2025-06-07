import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule, HttpHeaders } from '@angular/common/http';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { DataTable } from 'simple-datatables';
import { UserDetails } from '../models/UserModel';
import { WebsiteData } from '../models/WebsiteModels';
import { SslData } from '../models/SslModel';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-certificates',
  imports: [HttpClientModule,CommonModule,FormsModule],
  templateUrl: './certificates.component.html',
  styleUrl: './certificates.component.css'
})
export class CertificatesComponent implements OnInit {
         isOpen = false;
    isUploadOpen=false;
    isLoading: boolean = true;

  isUpdateModalOpen = false;
  selectedStudent: any = {};  // will store student info for editing


    userData : UserDetails | null = null;
    websites: WebsiteData [] = [];
    ssldata: SslData | null = null;
    website_id : number=0;
    website_name : string = '';

    url : string='';
    name : string='';

    constructor(private http : HttpClient ){

    }


    ngOnInit() {

      setTimeout(() => {
        this.isLoading = false;
      }, 100);

      this.GetWebsites();
      this.getProfile();

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

          this.website_id =this.websites[0]?.id;
          this.website_name = this.websites[0]?.name;
          this.GetSsl();

          console.log(".....................................................................");



        },
        error => {
          console.error('Error fetching websites:', error);
        }
      );
  } else {
    console.error('No token found. Cannot fetch websites.');
  }
}


GetSsl() {
  console.log("................");

  const token = localStorage.getItem('token');

  if (token) {
    const headers = new HttpHeaders({
      'Authorization': `Bearer ${token}`
    });

    this.http.get<SslData>(`http://localhost:5000/history/ssl/${this.website_id}`, { headers })
      .subscribe(
        response => {
          this.ssldata = response;
                   console.log("1.....................................................................");

          console.log(response);
                   console.log("1.....................................................................");

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



    initializeTable(): void {
      setTimeout(() => {
        let datatable = new DataTable('#search-table');
        console.log('Table initialized');
      }, 100);
    }

}
