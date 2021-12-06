#!/usr/bin/env ruby

require 'dotenv/load'
require 'dataverse'
require 'fileutils'
require 'csv'

ENV['DATA_DIR'] ||= '/opt/data'
ENV['COLLECTION'] ||= 'rdr'
ENV['ORCID_FILE'] ||= 'orcid.csv'

orcid_map = {}
CSV.foreach(File.join({ENV['DATA_DIR'], ENV['ORCID_FILE']) do |row|
  orcid_map[row.last.downcase] = row.first.downcase
end

root_dv = Dataverse::Dataverse.id(ENV['COLLECTION'])

storage_map = {}
error_ds = []

root_dv.each_dataset do |ds|
  authors = ds.metadata['author']
  unr = nil
  authors.each do |author|
    break if author['authorIdentifierScheme'] == 'ORCID' && unr = orcid_map[author['authorIdentifier']]
  end
  unless unr
    error_ds << ds.pid
    next
  end
  storage_map[unr] ||= 0
  storage_map[unr] += ds.size
end

ENV['REPORTS_DIR'] ||= File.join(ENV['DATA_DIR'], 'reports')
FileUtils.mkdir_p(ENV['REPORTS_DIR'])

now = DateTime.now

filepath = File.join(ENV['REPORTS_DIR'], "storage-#{now.strftime('%Y-%m-%d')}.csv")
File.open(filepath, 'wt') { |f| storage_map.each { |unr,size| f.puts "#{unr},#{size}" } }

filepath = File.join(ENV['REPORTS_DIR'], "storage-#{now.strftime('%Y-%m-%d')}.errors")
File.open(filepath, 'wt') { |f| error_ds.each { |id| f.puts "#{id}" } }
