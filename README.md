<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
<h3 align="center">Swift Cars</h3>

  <p align="center">
    Trafic simultation for ITESM course TC2008B
    <br />
    </p>
     <a href="https://github.com/pridapablo/swiftCars">
    <img src="Assets/TEC_Logo.svg" alt="Logo" width="80" height="80">
  </a>

  <p>
  <a href="https://github.com/pridapablo/swiftCars"><strong>Explore the repo »</strong></a>

  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#tech-stack">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Credits</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

This project is a traffic simulation for the course TC2008B at ITESM. The
simulation is done in Unity and the backend runs in Python.

Click here to watch a video of the simulation:

[![Watch the video][googledrive-shield]](https://drive.google.com/file/d/16s5Wneie261dGBbIs-P-Gt45KHIMrjaU/view?usp=sharing)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Tech Stack

#### Simulation

[![Unity][unity.com]][unity-url]
[![C#][c#.com]][c#-url]

#### Backend

[![Python][python.com]][python-url]

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->

## Getting Started

If you are interested in running the project locally, you can clone the repository and follow the instructions below:

### Prerequisites

<!-- Unity -->

- Unity 2022.3.12f1 LTS or higher
- [Unity Hub](https://unity3d.com/get-unity/download)

### Installation

Clone the repo

```sh
git clone
```

### Running the simulation

The simulation can be run in two modes: 2D and 3D, to run it in 3D the Unity
Editor should be booted and the scene `Assets/Scenes/BuildCity.unity` should be
opened. Start the server by running the file `server.py` in the folder
`Server` and then run the simulation in the Unity Editor.

If you want to run the simulation in 2D (mesa portrayal mode) just run the file
`server.py` with the flag `-m 2D`

For more information about the server run the command `python server.py -h`

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contact

#### **Colaborators: Team 2: "Swifties"**

- Fernanda Cortés Lozano - A01026613
- Pablo Banzo Prida - A01782031

#### **Instructors:**

- Gilberto Echeverría Furió
- Octavio Navarro Hinojosa

Project Link: [https://github.com/pridapablo/swiftCars](https://github.com/pridapablo/swiftCars)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GitHub Shields -->

[contributors-shield]: https://img.shields.io/github/contributors/pridapablo/swiftCars.svg?style=for-the-badge
[contributors-url]: https://github.com/pridapablo/swiftCars/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/pridapablo/swiftCars.svg?style=for-the-badge
[forks-url]: https://github.com/pridapablo/swiftCars/network/members
[stars-shield]: https://img.shields.io/github/stars/pridapablo/swiftCars.svg?style=for-the-badge
[stars-url]: https://github.com/pridapablo/swiftCars/stargazers
[issues-shield]: https://img.shields.io/github/issues/pridapablo/swiftCars.svg?style=for-the-badge
[issues-url]: https://github.com/pridapablo/swiftCars/issues
[license-shield]: https://img.shields.io/github/license/pridapablo/swiftCars.svg?style=for-the-badge
[license-url]: https://github.com/pridapablo/swiftCars/blob/master/LICENSE.txt

<!-- Stack Shields -->
<!-- Web Shields -->

[googledrive-shield]: https://img.shields.io/badge/Google%20Drive-4285F4?style=for-the-badge&logo=googledrive&logoColor=white
[bootstrap.com]: https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white
[bootstrap-url]: https://getbootstrap.com
[css3.com]: https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white
[css3-url]: https://developer.mozilla.org/en-US/docs/Web/CSS
[html.com]: https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white
[html-url]: https://developer.mozilla.org/en-US/docs/Web/HTML
[javascript.com]: https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black
[javascript-url]: https://developer.mozilla.org/en-US/docs/Web/JavaScript

<!-- Game Shields -->

[unity.com]: https://img.shields.io/badge/Unity-100000?style=for-the-badge&logo=unity&logoColor=white
[unity-url]: https://unity.com/
[c#.com]: https://img.shields.io/badge/C%23-239120?style=for-the-badge&logo=c-sharp&logoColor=white
[c#-url]: https://docs.microsoft.com/en-us/dotnet/csharp/
[python.com]: https://img.shields.io/badge/Python-14354C?style=for-the-badge&logo=python&logoColor=white
[python-url]: https://www.python.org/

<!-- Database Shields -->

[mysql.com]: https://img.shields.io/badge/MySQL-00000F?style=for-the-badge&logo=mysql&logoColor=white
[mysql-url]: https://www.mysql.com/
