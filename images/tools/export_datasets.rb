require 'dotenv/load'
require 'dataverse'
require 'fileutils'

root_dv = Dataverse::Dataverse.id('kul')

root_dv.each_dataset do |ds|
  data = ds.export_metadata('rdm')
  filename = "data/exports/#{ds['identifier']}.json"
  FileUtils.mkdir_p(File.dirname(filename))
  puts "#{filename}"
  File.open(filename, 'wt') { |f| f.write JSON.pretty_generate(data) }
end
