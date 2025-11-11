# Android Employee Manager - Quick Reference

## Project Statistics

- **Total Files**: 52
- **Kotlin Files**: 28
- **XML Resources**: 21
- **Configuration Files**: 6
- **Documentation**: 3

## Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    UI Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │  Splash     │  │    Auth     │  │    Main     │ │
│  │  Activity   │→ │  Activity   │→ │  Activity   │ │
│  └─────────────┘  └─────────────┘  └──────┬──────┘ │
│                                            │        │
│                    ┌───────────────────────┘        │
│                    ▼                                │
│  ┌─────────────────────────────────────────────┐   │
│  │         Navigation Component                 │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │Dashboard │  │ Employee │  │Attendance│  │   │
│  │  │ Fragment │  │ Fragment │  │ Fragment │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  │   │
│  │  ┌──────────┐  ┌──────────┐                │   │
│  │  │  Leave   │  │ Profile  │                │   │
│  │  │ Fragment │  │ Fragment │                │   │
│  │  └──────────┘  └──────────┘                │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                 ViewModel Layer                      │
│  ┌─────────────────────────────────────────────┐   │
│  │          DashboardViewModel                  │   │
│  │  (More ViewModels to be added)               │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                Repository Layer                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  EmployeeRepository  │  DepartmentRepository│   │
│  │  (More Repositories to be added)             │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────┐
│                   Data Layer                         │
│  ┌─────────────────────────────────────────────┐   │
│  │              Room Database                   │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  │   │
│  │  │Employee  │  │Department│  │Attendance│  │   │
│  │  │   DAO    │  │   DAO    │  │   DAO    │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  │   │
│  │  ┌──────────┐                               │   │
│  │  │  Leave   │                               │   │
│  │  │   DAO    │                               │   │
│  │  └──────────┘                               │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Database Schema

```
┌─────────────────────┐
│     Department      │
│─────────────────────│
│ id (PK)            │
│ departmentName     │◄────────┐
│ departmentCode     │          │
│ managerName        │          │
└─────────────────────┘          │
                                 │ FK
┌─────────────────────┐          │
│      Employee       │          │
│─────────────────────│          │
│ id (PK)            │          │
│ employeeId (UQ)    │──────────┘
│ fullName           │
│ email              │
│ phoneNumber        │
│ position           │
│ departmentId (FK)  │
│ salary             │
│ dateOfJoining      │
│ address            │
│ photoUri           │
│ isActive           │
│ createdAt          │
│ updatedAt          │
└─────────────────────┘
         │
         │ FK
         ├──────────────┐
         │              │
         ▼              ▼
┌─────────────────────┐  ┌─────────────────────┐
│     Attendance      │  │       Leave         │
│─────────────────────│  │─────────────────────│
│ id (PK)            │  │ id (PK)            │
│ employeeId (FK)    │  │ employeeId (FK)    │
│ date               │  │ leaveType          │
│ checkInTime        │  │ startDate          │
│ checkOutTime       │  │ endDate            │
│ status             │  │ reason             │
│ notes              │  │ status             │
│ locationLatitude   │  │ approvedBy         │
│ locationLongitude  │  │ createdAt          │
└─────────────────────┘  │ updatedAt          │
                         └─────────────────────┘
```

## Key Features Implemented

### ✅ Data Layer
- Room entities with proper relationships
- Type-safe DAOs with Flow support
- Repository pattern
- Type converters for Date and Enums

### ✅ Dependency Injection
- Hilt configuration
- Database module
- Singleton scope

### ✅ UI Components
- Material Design 3 theming
- ViewBinding & DataBinding
- Navigation Component
- Bottom Navigation
- Fragment-based architecture

### ✅ Resources
- Indonesian language strings
- Custom color scheme
- Responsive layouts
- File provider configuration

## Project Commands

```bash
# Open in Android Studio
File > Open > Select android-app directory

# Build debug APK
./gradlew assembleDebug

# Build release APK
./gradlew assembleRelease

# Run tests
./gradlew test

# Install on device
./gradlew installDebug

# Clean build
./gradlew clean
```

## File Locations

```
android-app/
├── README.md                           # Setup guide
├── IMPLEMENTATION.md                   # Technical details
├── QUICKREF.md                        # This file
│
├── app/src/main/
│   ├── AndroidManifest.xml            # App configuration
│   │
│   ├── java/com/ikodio/employeemanager/
│   │   ├── EmployeeManagerApplication.kt
│   │   │
│   │   ├── data/
│   │   │   ├── local/
│   │   │   │   ├── dao/              # 4 DAO files
│   │   │   │   ├── entities/         # 4 Entity files
│   │   │   │   └── database/         # 2 Database files
│   │   │   └── repository/           # 2 Repository files
│   │   │
│   │   ├── ui/
│   │   │   ├── splash/               # SplashActivity
│   │   │   ├── auth/                 # AuthActivity
│   │   │   ├── MainActivity.kt       # Main container
│   │   │   ├── dashboard/            # DashboardFragment
│   │   │   ├── employee/             # EmployeeListFragment
│   │   │   ├── attendance/           # AttendanceFragment
│   │   │   ├── leave/                # LeaveFragment
│   │   │   └── profile/              # ProfileFragment
│   │   │
│   │   ├── viewmodel/                # DashboardViewModel
│   │   └── di/                       # DatabaseModule
│   │
│   └── res/
│       ├── layout/                   # 8 layout files
│       ├── values/                   # strings, colors, themes
│       ├── navigation/               # nav_graph.xml
│       ├── menu/                     # bottom_navigation_menu.xml
│       ├── drawable/                 # splash_background.xml
│       └── xml/                      # 3 config files
│
└── build.gradle.kts                  # Dependencies
```

## Dependencies Overview

| Category | Library | Version | Purpose |
|----------|---------|---------|---------|
| Core | Kotlin | 1.9.20 | Language |
| UI | Material Design 3 | 1.11.0 | Components |
| Database | Room | 2.6.1 | Local storage |
| DI | Hilt | 2.48 | Injection |
| Async | Coroutines | 1.7.3 | Threading |
| Navigation | Navigation Component | 2.7.5 | Navigation |
| Image | Coil | 2.5.0 | Loading |
| Charts | MPAndroidChart | 3.1.0 | Graphs |
| PDF | iText | 7.2.5 | Generation |
| Excel | Apache POI | 5.2.5 | Export |
| Security | Security Crypto | 1.1.0 | Encryption |

## Status Enums

### AttendanceStatus
- `HADIR` - Present
- `IZIN` - Permission
- `SAKIT` - Sick
- `ALFA` - Absent

### LeaveType
- `CUTI` - Leave
- `SAKIT` - Sick Leave
- `IZIN` - Permission

### LeaveStatus
- `PENDING` - Awaiting approval
- `APPROVED` - Approved
- `REJECTED` - Rejected

## Next Development Steps

1. **Create RecyclerView Adapter** for employee list
2. **Implement Form Validation** for employee CRUD
3. **Add Image Picker** for employee photos
4. **Implement Search/Filter** functionality
5. **Create Detail Screens** with ViewPager
6. **Add Attendance Features** with GPS
7. **Implement Leave Workflow** with notifications
8. **Generate Reports** (PDF/Excel)
9. **Add Charts** to dashboard
10. **Write Tests** for all layers

## Important Notes

- All strings are in **Indonesian (Bahasa Indonesia)**
- Min SDK: **24** (Android 7.0)
- Target SDK: **34** (Android 14)
- Architecture: **MVVM**
- Database: **Room**
- DI: **Hilt**

## Support

- Repository: https://github.com/Hylmii/ERP-IKODIO
- Package: com.ikodio.employeemanager
- Email: support@ikodio.com

---

**Last Updated**: November 2025  
**Status**: Foundation Complete  
**Ready for**: Feature Implementation
