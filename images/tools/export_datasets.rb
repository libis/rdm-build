#!/usr/bin/env ruby

require 'dotenv/load'
require 'dataverse'
require 'fileutils'

root_dv = Dataverse::Dataverse.id('rdr')

root_dv.each_dataset do |ds|
  next unless ds.version(:published)
  data = ds.export_metadata('rdm')
  filename = "exports/#{ds['identifier']}.json"
  filepath = "#{ENV['DATA_DIR']}/#{filename}"
  FileUtils.mkdir_p(File.dirname(filepath))
  puts "#{filename}"
  File.open(filepath, 'wt') { |f| f.write JSON.pretty_generate(data) }
end
