# ACE

ACE, the Artificial Consciousness Engine, is a digital assistant. It is designed to help you with your daily tasks and keep you in the loop with your life and the world.

## Getting Started

These instructions will get you up and running with ACE on your local machine.

### Prerequisites

- Python 3.10 or higher
- Virtual environment (recommended)

_Note: This project is developed and tested on Python 3.10.2, in Windows 10. It may work on other versions and operating systems, but it is not guaranteed._

### Installing

1.  Clone the repository:

    ```bash
    git clone https://github.com/IllyShaieb/ACE.git
    ```

2.  Create a virtual environment (optional but recommended):

    ```bash
    python -m venv .venv
    ```

3.  Activate the virtual environment:

    ```bash
    # On Windows
    .venv\Scripts\activate
    ```

4.  Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5.  Create a `.env` file in the root directory of the project and add the following environment variables:

    ```env
    ACE_WEATHER_API_KEY=your_api_key_here
    ACE_HOME_LOCATION=your_home_location_here
    ```

### Running ACE

1.  Make sure your virtual environment is activated.
2.  Run the main script:

    ```bash
    python main.py
    ```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [CalVer](https://calver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/IllyShaieb/ACE/tags).

## Authors

- **Illy Shaieb** - [IllyShaieb](https://github.com/IllyShaieb)

## License

This project is licensed under the GNU General Public License version 3 (GPLv3) - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

We have used the following resources to build ACE:

- [WeatherAPI](https://www.weatherapi.com/) - For weather data
