# Ikodio Employee Manager - Android App

A comprehensive Android application for employee management with features for CRUD operations, attendance tracking, leave management, and more.

## 📱 Features

### Core Features
- ✅ **Employee Management**: Complete CRUD operations with validation
- ✅ **Attendance System**: Check-in/out with timestamps and GPS location
- ✅ **Leave Management**: Request and approval workflow
- ✅ **Department Management**: Manage departments and assignments
- ✅ **Dashboard**: Statistics and quick actions
- ✅ **Profile Management**: User profile and settings

### Technical Features
- ✅ MVVM Architecture
- ✅ Room Database for local storage
- ✅ Hilt for Dependency Injection
- ✅ Kotlin Coroutines & Flow
- ✅ Material Design 3
- ✅ Navigation Component
- ✅ ViewBinding & DataBinding

## 🛠️ Tech Stack

- **Language**: Kotlin
- **Architecture**: MVVM (Model-View-ViewModel)
- **Database**: Room Database
- **DI**: Hilt
- **Async**: Coroutines + Flow
- **UI**: Material Design 3, XML Layouts
- **Navigation**: Navigation Component
- **Image Loading**: Coil
- **Charts**: MPAndroidChart
- **PDF**: iText
- **Excel**: Apache POI
- **Min SDK**: 24 (Android 7.0)
- **Target SDK**: 34 (Android 14)

## 📁 Project Structure

```
app/
├── data/
│   ├── local/
│   │   ├── dao/              # Data Access Objects
│   │   ├── entities/         # Room entities
│   │   └── database/         # Database configuration
│   ├── repository/           # Repository pattern
│   └── model/                # Data models
├── ui/
│   ├── auth/                 # Authentication screens
│   ├── dashboard/            # Dashboard
│   ├── employee/             # Employee management
│   ├── attendance/           # Attendance tracking
│   ├── leave/                # Leave management
│   ├── department/           # Department management
│   ├── reports/              # Reports and analytics
│   └── profile/              # User profile
├── viewmodel/                # ViewModels
├── utils/                    # Utility classes
├── di/                       # Dependency Injection
└── navigation/               # Navigation configuration
```

## 🚀 Getting Started

### Prerequisites

- Android Studio Hedgehog (2023.1.1) or later
- JDK 17 or higher
- Android SDK with API level 34
- Gradle 8.2+

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Hylmii/ERP-IKODIO.git
cd ERP-IKODIO/android-app
```

2. Open the project in Android Studio

3. Sync Gradle files (Android Studio will prompt this automatically)

4. Build and run the app on an emulator or physical device

### Building the APK

To build a debug APK:
```bash
./gradlew assembleDebug
```

To build a release APK:
```bash
./gradlew assembleRelease
```

The APK will be generated in `app/build/outputs/apk/`

## 📊 Database Schema

### Employee Table
- id (Primary Key)
- employeeId (Unique)
- fullName
- email
- phoneNumber
- position
- departmentId (Foreign Key)
- salary
- dateOfJoining
- address
- photoUri
- isActive
- createdAt
- updatedAt

### Department Table
- id (Primary Key)
- departmentName
- departmentCode
- managerName

### Attendance Table
- id (Primary Key)
- employeeId (Foreign Key)
- date
- checkInTime
- checkOutTime
- status (HADIR/IZIN/SAKIT/ALFA)
- notes
- locationLatitude
- locationLongitude

### Leave Table
- id (Primary Key)
- employeeId (Foreign Key)
- leaveType (CUTI/SAKIT/IZIN)
- startDate
- endDate
- reason
- status (PENDING/APPROVED/REJECTED)
- approvedBy
- createdAt
- updatedAt

## 🔒 Permissions

The app requires the following permissions:
- `INTERNET` - For network operations
- `ACCESS_NETWORK_STATE` - To check network connectivity
- `CAMERA` - For photo capture
- `READ_EXTERNAL_STORAGE` - To read images (Android 12 and below)
- `WRITE_EXTERNAL_STORAGE` - To save files (Android 9 and below)
- `READ_MEDIA_IMAGES` - To read images (Android 13+)
- `ACCESS_FINE_LOCATION` - For GPS-based attendance
- `ACCESS_COARSE_LOCATION` - For approximate location
- `USE_BIOMETRIC` - For biometric authentication

## 🧪 Testing

Run unit tests:
```bash
./gradlew test
```

Run instrumented tests:
```bash
./gradlew connectedAndroidTest
```

## 📝 Form Validations

### Employee Form
- **Name**: Required, minimum 3 characters
- **Email**: Required, valid email format
- **Phone**: Required, valid format
- **Position**: Required
- **Department**: Required (dropdown)
- **Salary**: Number input
- **Date of Joining**: DatePicker
- **Address**: Textarea

## 🎨 UI Components

- Material Design 3 components
- Bottom Navigation for main sections
- FloatingActionButton for quick actions
- RecyclerView for lists
- ViewPager for tabbed interfaces
- Date/Time Pickers
- Loading states with ProgressBar
- Empty states with illustrations
- Error handling with Snackbar/Dialog

## 🌐 Localization

All strings are in Indonesian (Bahasa Indonesia) as per requirements.
String resources are located in `res/values/strings.xml`

## 🔐 Security Features

- EncryptedSharedPreferences for secure storage
- Password hashing (planned)
- Biometric authentication support
- SQL injection prevention through Room
- Session management

## 📦 Dependencies

Key dependencies include:
- AndroidX Core, AppCompat, ConstraintLayout
- Material Design Components
- Room Database
- Hilt for Dependency Injection
- Kotlin Coroutines
- Navigation Component
- Coil for image loading
- MPAndroidChart for charts
- iText for PDF generation
- Apache POI for Excel operations

See `app/build.gradle.kts` for complete list.

## 🚧 Development Status

This is a foundational implementation with core architecture in place:
- ✅ Project structure created
- ✅ Database layer (Room) implemented
- ✅ Repository pattern implemented
- ✅ Dependency injection (Hilt) configured
- ✅ Basic UI screens created
- ✅ Navigation configured
- ⏳ Full UI implementation (in progress)
- ⏳ Business logic implementation (in progress)
- ⏳ Testing suite (planned)

## 📄 License

This project is proprietary software owned by Ikodio.

## 👥 Team

- **Development Team**: Ikodio Engineering
- **Platform**: Android

## 📞 Support

For support and questions:
- Email: support@ikodio.com
- Repository: https://github.com/Hylmii/ERP-IKODIO

---

**Built with ❤️ by Ikodio Team**
