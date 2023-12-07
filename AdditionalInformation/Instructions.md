Instructions to run the Optimization-Simulation model in background from the server machine.

## ADPSO-CL methodology

1. To activate the listener service where the server will store the global best solution sent by the machines.
* In Powershell, in the repository path "dirty_pso_optimization_server", put:
  ```
  cargo build
  cargo run
  ```
* Don't close the terminal.

#### In other terminal:

2. Host machines:
```
Set-Item WSMan:\localhost\Client\TrustedHosts -Value 'vm2, vm3, vm4, vm5, vm6, vm7, vm8, vm9, vm10, vm11, vm12, vm13, vm14, vm15, vm16, vm17, vm18, vm19, vm20, vm21'
```

3. To verify hosts:
(Get-Item WSMan:\localhost\Client\TrustedHosts).value

4. To update repository:
```
foreach($i in 2..21){“Update git in vm$i”
Invoke-Command -ComputerName “vm$i” -ScriptBlock {cd C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\; git pull}}
```

5. To check outputs:
```
foreach($i in 2..21){“Check iterations in vm$i”
Invoke-Command -ComputerName “vm$i” -ScriptBlock {cd C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\ADPSO_CL\output; ls}}
```

6. To send the execution order:
```
foreach($i in 2..21){“Activate virtual environment in vm$i and send the order”
Invoke-Command -ComputerName “vm$i” -ScriptBlock {cd C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\ADPSO_CL; .\sp\Scripts\activate; powershell './Run_ADPSO_CL.ps1 0 201 202'} -AsJob}
```

## ADDE-CL methodology

#### In Powershell terminal:

1. Host machines:
```
Set-Item WSMan:\localhost\Client\TrustedHosts -Value 'vm2, vm3, vm4, vm5, vm6, vm7, vm8, vm9, vm10, vm11, vm12, vm13, vm14, vm15, vm16, vm17, vm18, vm19, vm20, vm21'
```

2. To verify hosts:
(Get-Item WSMan:\localhost\Client\TrustedHosts).value

3. To update repository:
```
foreach($i in 2..21){“Update git in vm$i”
Invoke-Command -ComputerName “vm$i” -ScriptBlock {cd C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\; git pull}}
```

4. To check outputs:
```
foreach($i in 2..21){“Check iterations in vm$i”
Invoke-Command -ComputerName “vm$i” -ScriptBlock {cd C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\ADDE_CL\output; ls}}
```

5. To active listener service on each machine:
```
foreach($i in 2..21){“Cargo run in vm$i”
Invoke-Command -ComputerName “vm$i” -ScriptBlock {cd C:\Users\vagrant\Documents\tcp_server; powershell ‘./Cargo_run_ADDE_CL.ps1’} -AsJob}
```

6. To send the execution order:
```
foreach($i in 2..21){“Activate virtual environment in vm$i and send the order”
Invoke-Command -ComputerName “vm$i” -ScriptBlock {cd C:\Users\vagrant\Documents\VA_InverseOptimizationProblem\ADDE_CL; .\sp\Scripts\activate; powershell './Run_ADDE_CL.ps1 0 201 202 20'} -AsJob}
```
