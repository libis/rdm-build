#!/usr/bin/env ruby

require 'dotenv/load'
require 'dataverse'
require 'fileutils'
require 'json'

class CustomProperties

  attr_reader :custom_dir, :target_dir

  def initialize(custom_dir, target_dir)
    @custom_dir = custom_dir
    @target_dir = target_dir
  end

  def process
    puts "Applying customizations from #{custom_dir} ..."
    Dir.glob(File.join(custom_dir, '*.json')).each do |file|
      data = JSON.parse(File.read(file), symbolize_names: true)
      puts "  ... #{File.basename(file, '.*')}"
      data[:data].each do |x|
        filename, name = x[:name].split('#')
        puts "      - #{filename} #{name}"
        found = false
        inplace_edit File.join(target_dir, filename), '' do |line|
          if line =~ /^#{name}=/
            line = "#{name}=#{x[:value]}"
            found = true
          end
          puts line
        end
        File.open(File.join(target_dir, filename), 'a') do |f|
          f.puts "#{name}=#{x[:value]}"
        end unless found
      end
    end
  end

  private

  def inplace_edit(file, bak, &block)
    old_stdout = $stdout
    argf = ARGF.clone

    argf.argv.replace [file]
    argf.inplace_mode = bak
    argf.each_line do |line|
      yield line
    end
    argf.close

    $stdout = old_stdout
  end

end

unless ARGV.size == 2
  puts "Usage: #{$PROGRAM_NAME} <customizations directory> <target properties directory>"
  exit 0
end

CustomProperties.new(ARGV[0], ARGV[1]).process
