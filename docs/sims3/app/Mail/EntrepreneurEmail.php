<?php

namespace App\Mail;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Mail\Mailable;
use Illuminate\Mail\Mailables\Content;
use Illuminate\Mail\Mailables\Envelope;
use Illuminate\Queue\SerializesModels;

class EntrepreneurEmail extends Mailable
{
    use Queueable, SerializesModels;
    public $title;
    public $body;
    public $cashier;
    /**
     * Create a new message instance.
     */
    public function __construct($title,$body,$cashier)
    {
        $this->body=$body;
        $this->title= $title;
        $this->cashier = $cashier;

    }

    /**
     * Get the message envelope.
     */
    public function envelope(): Envelope
    {
        return new Envelope(
            subject: 'Info about '. $this->title
        );
    }

    /**
     * Get the message content definition.
     */
    public function content(): Content
    {
        $status ="";
        if ($this->title=="site_closure")
        {
            $status = 'emails.siteClose';
        }
        elseif ($this->title =="entrepreneur_resignation")
        {
            $status = 'emails.entrepreneurResign';
        }
        elseif($this->title=="new_entrepreneur_coming")
        {
            $status = 'emails.newEntrepreneur';
        }
        elseif($this->title=="site_reopen")
        {
            $status = 'emails.siteOpen';
        }
        return new Content(
            markdown: $status,
        );
    }

    /**
     * Get the attachments for the message.
     *
     * @return array<int, \Illuminate\Mail\Mailables\Attachment>
     */
    public function attachments(): array
    {
        return [];
    }
}
