# Software environment

## Hardware
- CPU: Intel Core i7-14700K (3.40 GHz)
- RAM: 32.0 GB (31.7 GB usable)
- OS: Windows 11 Enterprise 25H2 (Build 26200.8037)

## Runtimes — locked

| Language   | Tool            | Version   | Compile / Run flags       |
|------------|-----------------|-----------|---------------------------|
| C          | GCC (WinLibs)   | 14.3.0    | gcc -O2                   |
| Rust       | rustc           | 1.94.0    | cargo build --release     |
| Go         | Go compiler     | 1.26.1    | go build                  |
| Java       | OpenJDK         | 21.0.10    | javac / java -server      |
| JavaScript | Node.js (V8)    | 24.14.0   | node --jitless=false      |
| Python     | CPython         | 3.12.10   | python                    |

### Verified on 2026-03-18
```
gcc.exe (MinGW-W64 x86_64-ucrt-posix-seh, built by Brecht Sanders) 14.3.0
rustc 1.94.1 (4a4ef493e 2026-03-02)
cargo 1.94.0 (85eff7c80 2026-01-15)
go version go1.26.1 windows/amd64
openjdk 21.0.10 2026-01-20 LTS
v24.14.0
Python 3.12.10
```


## Key Python packages
| Package      | Version  | Purpose                        | Link                   |
|--------------|----------|--------------------------------|------------------------|
| codecarbon   | 3.2.4    | CO2 emission estimation        |    |
| pyRAPL       | 0.2.3.1  | Intel RAPL energy measurement  | https://pypi.org/project/pyRAPL/ |
| psutil       | 7.2.2    | CPU + memory monitoring        |    |
| scipy        | 1.17.1   | Statistical tests              |    |
| pandas       | 3.0.1    | Data manipulation              |    |
| numpy        | 2.4.3    | Numerical computation          |    |
| matplotlib   | 3.10.8   | Figures and plots              |    |
| seaborn      | 0.13.2   | Statistical visualizations     |    |
| jupyter      | 1.1.1    | Exploratory analysis notebooks |    |


## Notes
- pyRAPL requires admin privileges to access Intel RAPL registers on Windows
- Rust uses GNU target for GCC toolchain consistency
- Node.js must be pinned via nvm 



## Commands to run files
### Run C files
- Go to \implements\c
- enter 
```
gcc -O2 -o bin/summation.exe summation.c
```
- run and again enter 
```
bin\summation.c
```

### Run go files
```
go run summation.go
```

### Run Rust file
- For each file
```
cargo run --release
```

### Run Jave file
```
javac summation.java
java summation
```