param()

$vm = [int]((hostname) -replace '\D+(\d+)','$1')
$ip = 10+$vm

#Write-Host $vm
cargo run -- --ip "10.0.0.$ip" --port 8888 --service DE --subnet 10.0.0