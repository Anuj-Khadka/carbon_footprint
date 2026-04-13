```
package main

import (
    "bufio"
    "fmt"
    "os"
)

const N = 100

var arr [N]int64

func setup() { ... }
func algorithm() int64 { ... }

func main() {
    setup()

    fmt.Println("ready")

    scanner := bufio.NewScanner(os.Stdin)
    for scanner.Scan() {
        fmt.Println(algorithm())
    }
}
```