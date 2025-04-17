  
. /opt/homebrew/Caskroom/miniconda/base/etc/profile.d/conda.sh

conda activate transpod

cd $HOME/repos/transpod

./nightly.sh &> nightly$(date +"%Y_%m_%d_%I_%M_%p").log


