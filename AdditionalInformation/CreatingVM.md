This file contains information for creating a base virtual machine (VM).

**Software installation:**

1. Install Vagrant [version 2.3.1](https://developer.hashicorp.com/vagrant/downloads) with the default configuration. 
    * Afterwards, restart the computer.
    * In Powershell, verify the installation with the following instruction: 
    ```
    vagrant
    ```

2. Install VirtualBox (version 6.1.38) and the “Extension Pack” of the same version. 
    * The extension pack is installed within the program.

**Virtual machine creation:**

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

**Virtual machine base configuration:**

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
