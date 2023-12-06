param($p1, $p2, $p3)

$iteration = [int]($p1)
$total_iteration = [int]($p2)
$final_iteration = [int]($p3)

$vm = [int]((hostname) -replace '\D+(\d+)','$1')

while($iteration -ne $total_iteration){
    
      #Write-Host "Run experiment : "$iteration
      #Get-Date -Format "dddd MM/dd/yyyy HH:mm K"
      python Methodology_ADPSO_CL.py 10.0.0.11:8888 $iteration $total_iteration $final_iteration $vm

      if($error.count -eq 0){
          $iteration++
          $error.clear()
      }
      else{
          Write-Host "Fallo ejecucion : "$iteration
      }
      #Write-Host "Experiment "$iteration " finished"
      #Get-Date -Format "dddd MM/dd/yyyy HH:mm K"
}
