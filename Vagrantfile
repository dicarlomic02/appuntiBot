VAGRANTFILE_API_VERSION="2"
Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
config.vm.box="ubuntu/bionic64"

   config.vm.define :server do |h1_config|
    h1_config.vm.hostname="server"
    h1_config.vm.network "private_network", ip: "192.168.100.100"
   end
end