This file contains information for creating a base virtual machine (VM).

### Software installation:

1. Install Vagrant [version 2.3.1](https://developer.hashicorp.com/vagrant/downloads) with the default configuration. 
    * Afterwards, restart the computer.
    * In Powershell, verify the installation with the following instruction: 
    ```
    vagrant
    ```

2. Install VirtualBox (version 6.1.38) and the “Extension Pack” of the same version. 
    * The extension pack is installed within the program.

### Virtual machine creation:

3. To create the base VM, the Vagrant public box ["windows-10-1709-base-winrm"](https://app.vagrantup.com/eyewaretech/boxes/windows-10-1709-base-winrm) is used, which has the Windows 10 operating system.
    * The advantage of this box is that it uses vagrant rdp to access the VM using Windows Remote Desktop Connection.
    * This box has a minimum configuration of RAM, hard drive, etc. However, these settings can be modified later.

4. In Powershell:
* Go to the path where the *vagrantfile* will be downloaded. Put the following instructions:
    ```
    vagrant init eyewaretech/windows-10-1709-base-winrm --box-version 0.0.1
    ```
    * With this instruction, that box is consumed from a vagrant repository.
    * When executed, a *vagrantfile* is created, where the description of the downloaded box is located.
* Execute the following instruction: 
    ```
    vagrant up
    ```
    * This command will take the "vagrant-file" to create the VM.

    NOTE: The hypervisor service must be enabled from the computer's bios, depending on the equipment configuration.

### Base VM configuration:

5. Configuration to execute remote instructions with *winrm*:
* Disable Firewalls in the control panel
* Change the network connection type to private. We do this from Powershell by executing the instruction:
    ```
    Set-NetConnectionProfile -NetworkCategory Private
    ```
* Restore the listener configuration by executing the following instructions:
    ```
    winrm invoke Restore winrm/Config
    ```
* Run the following command to make a default configuration of the Windows Remote Administration service and its listener:
    ```
    winrm quickconfig
    ```

6. Modify the hard disk size of the virtual machine. 
* By default, the "windows-10-1709-base-winrm" box is configured with a 40 GB hard disk.
* First, it is necessary to copy the disk in *.vmdk* format to *.vdi* format. In Powershell, we go to the path where VirtualBox is installed and put the following instruction:
    ```
    .\VBoxManage clonemedium "D:\...\VirtualBox VMs\eyewaretech-dev\box-disk001.vmdk" "D:\...\VirtualBox VMs\eyewaretech-dev\box- disk001.vdi" --format vdi
    ```
  NOTE: The used path is where the VM is located.

* We increased the size of the *.vdi* disk to 160 GB (160GB * 1024Mb):
    ```
    .\VBoxManage modifymedium "D:\...\VirtualBox VMs\eyewaretech-dev\box-disk001.vdi" --resize 163840
    ```
* We associate the disk in *.vdi* format to the virtual machine.
    * When the machine is turned off, in Settings - Storage - delete the disk in *.vmdk* format and add the new one.
    * Delete from PC the disk in *.vmdk* format with this instruction:
    ```
    rm "D:\...\VirtualBox VMs\eyewaretech-dev\box-disk001.vmdk"
    ```
    * On the machine: Go to "This PC", do right click and select "Disk Management" – "Expand volume".

7. Install WEAP
* Restore the WEAP model and the required version (*backup* file).

8. Install Git
* Is required to download/update/modify the repository that has the scripts that are used to send the order to the other virtual machines
* Download the necessary repositories (listed in [README.md](README.md)):
    * VA_InverseOptimizationProblem
    * tcp_server
    * dirty_pso_optimization_server. The IP of the machine that will be the server (VM1) must be changed to "10.0.0.11" in port: "8888".

9. The programming language "RUST" must be installed: 
* Install "Tools for Visual Studio", adding:
   * C++ Clang tools for Windows...
   * C++ Modules for v143 build tools...

10. Install Python and create a virtual environment within the repository with the necessary libraries to execute the Simulation-Optimization model in background.
* Also, add the following:
   ```
   python -m pip install -U pip setuptools
   pip install git+https://github.com/milocortes/request_rust_server@main
   ```
11. Add the folder that contains the MODFLOW executable to the repository.

12. Establish that the screen never turns off.

13. Disable updates for 30 days.

14. When the machine is off, check the RAM and the number of processors assigned to the virtual machine depending on the problem.

15. Configure network adapters when the machine is off:
* Private network to communicate with other nodes. In "Settings" - "Network" -  "Adapter 1" - Check "Enable Network Adapter".
* To communicate the host with the server. In "Settings" - "Network" -  "Adapter 2" - Check "Enable Network Adapter" - Select "Host-only Adapter" / "VirtualBox Host-Only Ethernet Adapter #2".

### VM to Vagrant box:

16. We convert the VM that is currently in VirtualBox into a Vagrant box:
* The VM in the base VirtualBox is called "eyewaretech-dev", and the box will be called "w10_distributed_methodologies.box".
   ```
   vagrant package --base=eyewaretech-dev --output=w10_distributed_methodologies.box
   ```
17. Copy the box to our local Vagrant environment.
   ```
   vagrant box add .\w10_distributed_methodologies.box. --name w10_distributed_methodologies
   ```
18. Create a minimal *Vagrantfile* by executing the following instruction:
   ```
   vagrant init –m
   ```

### Generate VMs:

19. Edit the *Vagrantfile* and create as many configuration areas as VMs are needed. For this example, we will create three VMs.
* With *vm.network*, it defines the IP address of each machine on a private network.
* With *vm.box*, it assigns which box will be used in the configuration of each VM.
* The Vagrantfile would look like this:
   ```
   # -*- mode: ruby -*-
   # vi: set ft=ruby :
   
   NODE_COUNT = 3
   Vagrant.configure("2") do |config|
     #Configure the machines
     #config.vm.network "forwarded_port" , host: 33390 , guest: 3389
     config.vm.usable_port_range = (2200..2350) 
     config.vm.communicator = "winrm"
     config.winrm.username = "vagrant"
     config.winrm.password = "vagrant"
   	
     config.vm.guest = :windows
     config.windows.halt_timeout = 1200
   
     (1..NODE_COUNT).each do |i|
   
       config.vm.define "node#{i}" do |subconfig|
       subconfig.vm.box = "w10_distributed_methodologies"
       subconfig.vm.hostname = "vm#{i}"
       subconfig.vm.network "private_network", ip: "10.0.0.#{i+10}"
   
       end
     
      end
   end
   ```
   
20. Execute the instruction to create and provision the VMs:
```
vagrant up
```
NOTE: It must be located in Powershell, in the path where the *vagrantfile* was created.
