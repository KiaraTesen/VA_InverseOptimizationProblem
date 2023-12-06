param($p1, $p2, $p3, $p4)

$iteration = [int]($p1)
$total_iteration = [int]($p2)
$final_iteration = [int]($p3)

$vms = [int]($p4)
$vm = [int]((hostname) -replace '\D+(\d+)','$1')

while($iteration -ne $total_iteration){
      #Write-Host "Run experiment : "$iteration
      #Get-Date -Format "dddd MM/dd/yyyy HH:mm K"
      
      python Methodology_ADDE_CL.py $vm $iteration $total_iteration $final_iteration $vms
      if($error.count -eq 0){
          print($iteration)
          $iteration++
          $error.clear()
      }
      else{
          print($iteration)
          Write-Host "Fallo ejecucion : "$iteration
      }
      #Write-Host "Experiment "$iteration " finished"
      #Get-Date -Format "dddd MM/dd/yyyy HH:mm K"
}